import json
import os
from models import ProjectState, ProjectTask, TaskStatus
from typing import Optional

STATE_FILE = "state.json"

class StateManager:
    def __init__(self, state_dir: str = "."):
        self.state_path = os.path.join(state_dir, STATE_FILE)
        self.state: Optional[ProjectState] = None

    def load_state(self) -> ProjectState:
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                data = json.load(f)
                self.state = ProjectState(**data)
        else:
            self.state = ProjectState(project_name="New Project")
            self.save_state()
        return self.state

    def save_state(self):
        if self.state:
            with open(self.state_path, "w") as f:
                f.write(self.state.model_dump_json(indent=2))

    def update_task(self, task_id: str, **kwargs):
        if not self.state:
            self.load_state()
        
        for task in self.state.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    setattr(task, key, value)
                break
        self.save_state()

    def add_task(self, task: ProjectTask):
        if not self.state:
            self.load_state()
        self.state.tasks.append(task)
        self.save_state()
