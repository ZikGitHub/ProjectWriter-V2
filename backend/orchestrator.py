import asyncio
from typing import List
from models import ProjectState, ProjectTask, TaskStatus
from state_manager import StateManager
from coder import Coder

class Orchestrator:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.coder = Coder(state_dir=state_manager.state_dir if hasattr(state_manager, 'state_dir') else "./generated_project")

    async def run_execution_loop(self):
        state = self.state_manager.load_state()
        
        while True:
            # 1. Identify tasks ready to run
            ready_tasks = [
                task for task in state.tasks 
                if task.status == TaskStatus.PENDING and 
                all(dep_id in state.completed_files for dep_id in task.requires) # simplified check
            ]
            
            # For simplicity, if no explicit provides/requires mapping, check if requires IDs are in completed tasks
            completed_task_ids = [t.id for t in state.tasks if t.status == TaskStatus.COMPLETED]
            ready_tasks = [
                task for task in state.tasks
                if task.status == TaskStatus.PENDING and
                all(dep_id in completed_task_ids for dep_id in task.requires)
            ]

            if not ready_tasks:
                if all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for task in state.tasks):
                    break
                await asyncio.sleep(2) # Wait for other tasks to complete
                state = self.state_manager.load_state()
                continue

            # 2. Run ready tasks in parallel
            execution_tasks = [self.execute_task(task) for task in ready_tasks]
            await asyncio.gather(*execution_tasks)
            
            # Refresh state
            state = self.state_manager.load_state()

    async def execute_task(self, task: ProjectTask):
        self.state_manager.update_task(task.id, status=TaskStatus.IN_PROGRESS)
        
        try:
            # Gather context from previous tasks if needed
            context = "Focus on modularity and clear interfaces."
            
            code = await self.coder.write_file(task, context)
            
            # Validate syntax
            is_valid = await self.coder.validate_syntax(task.file_path)
            
            if is_valid:
                self.state_manager.update_task(task.id, status=TaskStatus.COMPLETED)
            else:
                self.state_manager.update_task(task.id, status=TaskStatus.FAILED, error="Syntax validation failed")
                
        except Exception as e:
            self.state_manager.update_task(task.id, status=TaskStatus.FAILED, error=str(e))
