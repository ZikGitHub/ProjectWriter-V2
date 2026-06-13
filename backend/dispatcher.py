from typing import List, Dict, Any
from langgraph.types import Send
from models import TaskState, ProjectTask, TaskStatus, ProjectState

def dispatcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("DEBUG: Dispatcher node running.")
    tasks = state.get("tasks", [])
    completed_files: List[str] = state.get("completed_files", [])
    print(f"DEBUG: Tasks: {tasks}")
    print(f"DEBUG: Completed files: {completed_files}")
    
    # Identify tasks that are PENDING and have all dependencies met
    ready_tasks = [
        task for task in tasks
        if (task.get("status") if isinstance(task, dict) else task.status) == TaskStatus.PENDING and
        all(dep_id in completed_files for dep_id in (task.get("requires", []) if isinstance(task, dict) else task.requires))
    ]
    print(f"DEBUG: Ready tasks count: {len(ready_tasks)}")

    # Return as a dictionary that LangGraph understands as a command for edges
    return {
        "next": [
            Send("execute_node", TaskState(
                id=task.get("id") if isinstance(task, dict) else task.id,
                file_path=(task.get("file_path") if isinstance(task, dict) else task.file_path) or f"{(task.get('domain') if isinstance(task, dict) else task.domain)}/{(task.get('id') if isinstance(task, dict) else task.id)}.py",
                instruction=task.get("description") if isinstance(task, dict) else task.description,
                target_model="qwen2.5-coder:1.5b",
                current_code=None
            ))
            for task in ready_tasks
        ]
    }
