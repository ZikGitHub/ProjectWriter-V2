from langgraph.graph import StateGraph, END
from langgraph.types import Send
from models import ProjectState, TaskState, TaskStatus, ProjectTask
from dispatcher import dispatcher_node
from reducer import reducer_node
from state_manager import StateManager
from coder import Coder
from logger_config import get_logger
import asyncio

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        # Attempt to get state_dir, fallback to default if not available or via attribute
        self.state_dir = getattr(state_manager, 'state_dir', "./generated_project")
        self.coder = Coder(state_dir=self.state_dir)
        self.graph = self._build_graph()
        logger.info("Orchestrator V2 initialized.")

    def _build_graph(self):
        logger.debug("Building LangGraph workflow.")
        workflow = StateGraph(ProjectState)

        # Nodes
        workflow.add_node("dispatcher", dispatcher_node)
        workflow.add_node("execute_node", self.execute_task)
        workflow.add_node("reducer", reducer_node)

        # Edges
        workflow.set_entry_point("dispatcher")
        workflow.add_conditional_edges("dispatcher", self.route_tasks)
        workflow.add_edge("execute_node", "reducer")
        workflow.add_edge("reducer", "dispatcher")
        
        return workflow.compile()

    def route_tasks(self, state: ProjectState):
        tasks = state.get("tasks", [])
        if not any(t.get("status") == TaskStatus.PENDING for t in tasks):
            logger.info("No more pending tasks. Routing to END.")
            return END
        return "execute_node"

    async def run_execution_loop(self):
        logger.info("Starting V2 execution loop.")
        # pydantic_state is actually a dict from StateManager
        pydantic_state = self.state_manager.load_state()
        
        # Ensure it's a dict
        if hasattr(pydantic_state, 'model_dump'):
            # It's a Pydantic object
            state_dict = pydantic_state.model_dump()
        else:
            # It's a dict
            state_dict = pydantic_state

        initial_state = {
            "project_name": state_dict.get("project_name", "Unknown"),
            "version": state_dict.get("version", "2.0"),
            "tasks": state_dict.get("tasks", []),
            "completed_files": state_dict.get("completed_files", []),
            "updates": [],
            "metadata": state_dict.get("metadata", {})
        }
        await self.graph.ainvoke(initial_state, {"recursion_limit": 50})

    async def execute_task(self, task_state: TaskState):
        # Retrieve task info from state manager based on ID
        task_id = task_state.get("id")
        logger.info(f"V2 executing task: {task_id}")
        if not task_id:
            logger.warning("No task ID provided in task state.")
            return {"updates": [task_state]}
            
        task = next((t for t in self.state_manager.load_state().tasks if t.id == task_id), None)
        if not task:
            logger.error(f"Task {task_id} not found in state.")
            return {"updates": [task_state]}
            
        try:
            context = "Focus on modularity and clear interfaces."
            code = await self.coder.write_file(task, context)
            is_valid = await self.coder.validate_syntax(task.file_path)
            
            if is_valid:
                logger.info(f"Task {task_id} code generated and validated.")
                task_state["current_code"] = code
            else:
                logger.error(f"Task {task_id} syntax validation failed.")
                task_state["current_code"] = None
        except Exception as e:
            logger.error(f"Error in execute_task for {task_id}: {str(e)}")
            task_state["current_code"] = None
            
        return {"updates": [task_state]}
