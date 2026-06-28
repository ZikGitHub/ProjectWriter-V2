from typing import List, Dict, Any
from langgraph.types import Send
from models import TaskState, ProjectTask, TaskStatus, ProjectState
from logger_config import get_logger

logger = get_logger(__name__)

def dispatcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("Dispatcher node running.")
    # In LangGraph, state can be a dict or a Pydantic model
    tasks = state.tasks if hasattr(state, 'tasks') else state.get("tasks", [])
    completed_files: List[str] = state.completed_files if hasattr(state, 'completed_files') else state.get("completed_files", [])
    logger.debug(f"Tasks: {tasks}")
    logger.debug(f"Completed files: {completed_files}")
    
    # Identify tasks that are PENDING and have all dependencies met
    ready_tasks = []
    for task in tasks:
        status = task.status if hasattr(task, 'status') else task.get("status")
        requires = task.requires if hasattr(task, 'requires') else task.get("requires", [])
        
        if status == TaskStatus.PENDING and all(dep_id in completed_files for dep_id in requires):
            ready_tasks.append(task)

    logger.info(f"Ready tasks identified: {len(ready_tasks)}")

    # Return as a dictionary that LangGraph understands as a command for edges
    return {
        "next": [
            Send("execute_node", TaskState(
                id=task.id if hasattr(task, 'id') else task.get("id"),
                file_path=(task.file_path if hasattr(task, 'file_path') else task.get("file_path")) or f"{(task.domain if hasattr(task, 'domain') else task.get('domain'))}/{(task.id if hasattr(task, 'id') else task.get('id'))}.py",
                instruction=task.description if hasattr(task, 'description') else task.get("description"),
                target_model="qwen2.5-coder:1.5b",
                current_code=None
            ))
            for task in ready_tasks
        ]
    }
