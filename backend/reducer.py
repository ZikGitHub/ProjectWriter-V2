from typing import List, Dict, Any
from models import ProjectState, TaskState, TaskStatus
from logger_config import get_logger

logger = get_logger(__name__)

def reducer_node(state: ProjectState, updates: List[TaskState] = None) -> Dict[str, Any]:
    """
    Processes updates from the task execution and updates the state.
    """
    logger.debug("Reducer node running.")
    
    # Ensure state is a dict for internal processing if needed, or use attributes
    # LangGraph state is usually the actual state object or a dict.
    # In our implementation, ProjectState is a Pydantic model.
    
    actual_updates = updates if updates is not None else (state.updates if hasattr(state, 'updates') else [])
    
    if not actual_updates:
        logger.debug("No updates received.")
        return {}
    
    logger.info(f"Processing {len(actual_updates)} updates.")

    # Update tasks
    tasks = state.tasks if hasattr(state, 'tasks') else []
    completed_files = state.completed_files if hasattr(state, 'completed_files') else []

    for update in actual_updates:
        # Find the corresponding task
        task_id = update.get("id")
        task = next((t for t in tasks if (t.id if hasattr(t, 'id') else t.get('id')) == task_id), None)
        
        if task:
            is_task_dict = isinstance(task, dict)
            if update.get("current_code"):
                if is_task_dict:
                    task["status"] = TaskStatus.COMPLETED
                    task["file_path"] = update["file_path"]
                else:
                    task.status = TaskStatus.COMPLETED
                    task.file_path = update["file_path"]
                    
                current_id = task.id if not is_task_dict else task.get("id")
                if current_id not in completed_files:
                    completed_files.append(current_id)
                logger.info(f"Task {current_id} marked completed.")
            else:
                if is_task_dict:
                    task["status"] = TaskStatus.FAILED
                    task["error"] = "Code generation or validation failed."
                else:
                    task.status = TaskStatus.FAILED
                    task.error = "Code generation or validation failed."
                logger.error(f"Task {task.id if not is_task_dict else task.get('id')} marked failed.")
                
    # Return the updates to the state
    return {
        "completed_files": completed_files, 
        "updates": [] # Clear the updates channel
    }
