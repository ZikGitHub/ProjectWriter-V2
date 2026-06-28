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
        logger.debug(f"Routing tasks in Orchestrator V2. State: {state}")
        # Support both dict and Pydantic model state
        tasks = state.tasks if hasattr(state, 'tasks') else state.get("tasks", [])
        completed_files = state.completed_files if hasattr(state, 'completed_files') else state.get("completed_files", [])
        
        # Identify ready tasks (status is PENDING and all dependency task IDs are in completed_files)
        ready_tasks = []
        for task in tasks:
            is_dict = isinstance(task, dict)
            status = task.get("status") if is_dict else task.status
            requires = task.get("requires", []) if is_dict else task.requires
            
            if status == TaskStatus.PENDING and all(dep_id in completed_files for dep_id in requires):
                ready_tasks.append(task)
                
        if not ready_tasks:
            # If no tasks are pending or in progress, we are done
            pending_or_running = [
                t for t in tasks 
                if (t.get("status") if isinstance(t, dict) else t.status) in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
            ]
            if not pending_or_running:
                logger.info("No pending or in-progress tasks. Routing to END.")
                return END
            else:
                logger.info("No ready tasks, but pending/in-progress tasks exist. Routing to END to avoid deadlock.")
                return END
                
        logger.info(f"Routing {len(ready_tasks)} tasks to execute_node.")
        return [
            Send("execute_node", TaskState(
                id=task.get("id") if isinstance(task, dict) else task.id,
                file_path=(task.get("file_path") if isinstance(task, dict) else task.file_path) or f"{(task.get('domain') if isinstance(task, dict) else task.domain)}/{(task.get('id') if isinstance(task, dict) else task.id)}.py",
                instruction=task.get("description") if isinstance(task, dict) else task.description,
                target_model="qwen2.5-coder:1.5b",
                current_code=None
            ))
            for task in ready_tasks
        ]

    async def run_execution_loop(self):
        logger.info("Starting Orchestrator V2 execution loop via LangGraph.")
        state = self.state_manager.load_state()
        
        try:
            # Invoke the LangGraph workflow
            logger.info("Invoking LangGraph workflow...")
            final_state = await self.graph.ainvoke(state)
            
            # Update state with tasks and completed_files from the run
            if hasattr(final_state, 'tasks'):
                state.tasks = final_state.tasks
                state.completed_files = final_state.completed_files
                state.updates = final_state.updates
            elif isinstance(final_state, dict):
                state.tasks = [ProjectTask(**t) if isinstance(t, dict) else t for t in final_state.get("tasks", [])]
                state.completed_files = final_state.get("completed_files", [])
                state.updates = final_state.get("updates", [])
            
            # Save the final state back to disk
            self.state_manager.save_state()
            logger.info("Orchestrator V2 loop completed successfully.")
        except Exception as e:
            logger.error(f"Error during V2 execution loop: {str(e)}")
            raise

    async def execute_task(self, task_state: TaskState):
        task_id = task_state.get("id")
        file_path = task_state.get("file_path")
        instruction = task_state.get("instruction")
        domain = file_path.split("/")[0] if "/" in file_path else "api"
        
        logger.info(f"Executing task in Orchestrator V2: {task_id} ({file_path})")
        
        # Instantiate a ProjectTask to pass to Coder (which expects a ProjectTask object)
        task = ProjectTask(
            id=task_id,
            domain=domain,
            description=instruction,
            file_path=file_path,
            status=TaskStatus.IN_PROGRESS
        )
        
        try:
            # Gather context
            context = "Focus on modularity, high quality, and clear interfaces."
            
            # Write file using Coder
            code = await self.coder.write_file(task, context, state_dir=self.state_dir)
            
            # Validate syntax
            is_valid = await self.coder.validate_syntax(file_path, state_dir=self.state_dir)
            
            if is_valid:
                logger.info(f"Task {task_id} code generation and syntax validation completed successfully.")
                task_state["current_code"] = code
            else:
                logger.error(f"Task {task_id} syntax validation failed.")
                task_state["current_code"] = None
                
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            task_state["current_code"] = None
            
        return {"updates": [task_state]}

