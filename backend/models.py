from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, TypedDict, Annotated
import operator
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskState(TypedDict):
    id: str
    file_path: str
    instruction: str
    target_model: str
    current_code: Optional[str]

class ProjectTask(BaseModel):
    id: str
    domain: str
    description: str
    requires: List[str] = []
    provides: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    file_path: Optional[str] = None
    error: Optional[str] = None

class ProjectState(BaseModel):
    project_name: str = "New Project"
    version: str = "0.0.1"
    tasks: List[ProjectTask] = []
    completed_files: List[str] = []
    updates: List[TaskState] = []
    metadata: Dict[str, Any] = {}
