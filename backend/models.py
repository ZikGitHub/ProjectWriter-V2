from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

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
    project_name: str
    version: str = "2.0"
    tasks: List[ProjectTask] = []
    completed_files: List[str] = []
    dependency_graph: Dict[str, List[str]] = {}
    metadata: Dict[str, Any] = {}
