import json
import os
from models import ProjectState, ProjectTask, TaskStatus
from typing import Optional
from logger_config import get_logger

logger = get_logger(__name__)

STATE_FILE = "state.json"

class StateManager:
    def __init__(self, state_dir: str = "."):
        self.state_dir = state_dir
        self.state_path = os.path.join(state_dir, STATE_FILE)
        self.state: Optional[ProjectState] = None
        logger.info(f"StateManager initialized with path: {self.state_path}")

    def load_state(self) -> ProjectState:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r") as f:
                    data = json.load(f)
                    self.state = ProjectState(**data)
                logger.debug(f"State loaded from {self.state_path}")
            except Exception as e:
                logger.error(f"Error loading state from {self.state_path}: {str(e)}")
                self.state = ProjectState(project_name="Error Recovery")
        else:
            logger.info(f"State file not found at {self.state_path}, creating new state.")
            self.state = ProjectState(project_name="New Project")
            self.save_state()
        return self.state

    def save_state(self):
        if self.state:
            try:
                os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
                with open(self.state_path, "w") as f:
                    f.write(self.state.model_dump_json(indent=2))
                logger.debug(f"State saved to {self.state_path}")
            except Exception as e:
                logger.error(f"Error saving state to {self.state_path}: {str(e)}")

    def update_task(self, task_id: str, **kwargs):
        logger.info(f"Updating task {task_id} with {kwargs}")
        if not self.state:
            self.load_state()
        
        found = False
        for task in self.state.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    setattr(task, key, value)
                found = True
                break
        
        if found:
            self.save_state()
        else:
            logger.warning(f"Task {task_id} not found for update.")

    def add_task(self, task: ProjectTask):
        logger.info(f"Adding task: {task.id}")
        if not self.state:
            self.load_state()
        self.state.tasks.append(task)
        self.save_state()
