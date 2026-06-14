from typing import List, Dict, Any
from models import ProjectState, TaskState, TaskStatus
from logger_config import get_logger

logger = get_logger(__name__)

def reducer_node(state: ProjectState, updates: List[TaskState] = None) -> Dict[str, Any]:
    """
    Processes updates from the task execution and updates the state.
    """
    logger.debug("Reducer node running.")
    # Use provided updates or extract from state
    actual_updates = updates if updates is not None else state.get("updates", [])
    
    if not actual_updates:
        logger.debug("No updates received.")
        return {}
    
    logger.info(f"Processing {len(actual_updates)} updates.")

    # Update tasks based on the updates channel
    tasks = state.get("tasks", [])
    completed_files = state.get("completed_files", [])

    for update in actual_updates:
        # Find the corresponding task
        task = next((t for t in tasks if t.get("id") == update.get("id")), None)
        
        if task:
            if update.get("current_code"):
                task["status"] = TaskStatus.COMPLETED
                task["file_path"] = update["file_path"]
                if task.get("id") not in completed_files:
                    completed_files.append(task.get("id"))
                logger.info(f"Task {task.get('id')} marked completed.")
            else:
                task["status"] = TaskStatus.FAILED
                task["error"] = "Code generation or validation failed."
                logger.error(f"Task {task.get('id')} marked failed.")
                
    # Return the updates to the state
    return {
        "completed_files": completed_files, 
        "updates": [] # Clear the updates channel
    }
