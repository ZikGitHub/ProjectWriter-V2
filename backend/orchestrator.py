import asyncio
from typing import List
from models import ProjectState, ProjectTask, TaskStatus
from state_manager import StateManager
from coder import Coder
from logger_config import get_logger

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.coder = Coder(state_dir=state_manager.state_dir if hasattr(state_manager, 'state_dir') else "./generated_project")
        logger.info("Orchestrator initialized.")

    async def run_execution_loop(self):
        logger.info("Starting execution loop.")
        # State is a dict
        state = self.state_manager.load_state()
        
        # Access as dict
        tasks_data = state.get("tasks", [])
        completed_files = state.get("completed_files", [])
        
        # We need task objects... but we have dicts.
        # Let's recreate them if needed, or update the logic to handle dicts.
        # The simplest is to use pydantic to parse them back.
        from models import ProjectTask
        tasks = [ProjectTask(**t) if isinstance(t, dict) else t for t in tasks_data]
        
        while True:
            # 1. Identify tasks ready to run
            completed_task_ids = [t.id for t in tasks if t.status == TaskStatus.COMPLETED]
            
            ready_tasks = [
                task for task in tasks
                if task.status == TaskStatus.PENDING and
                all(dep_id in completed_task_ids for dep_id in task.requires)
            ]

            if not ready_tasks:
                if all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for task in tasks):
                    logger.info("All tasks completed or failed. Ending loop.")
                    break
                logger.debug("No ready tasks, waiting...")
                await asyncio.sleep(2) # Wait for other tasks to complete
                state = self.state_manager.load_state()
                tasks_data = state.get("tasks", [])
                tasks = [ProjectTask(**t) if isinstance(t, dict) else t for t in tasks_data]
                continue

            logger.info(f"Executing {len(ready_tasks)} ready tasks.")
            # 2. Run ready tasks in parallel
            execution_tasks = [self.execute_task(task) for task in ready_tasks]
            await asyncio.gather(*execution_tasks)
            
            # Refresh state
            state = self.state_manager.load_state()
            tasks_data = state.get("tasks", [])
            tasks = [ProjectTask(**t) if isinstance(t, dict) else t for t in tasks_data]

    async def execute_task(self, task: ProjectTask):
        logger.info(f"Executing task: {task.id} ({task.file_path})")
        self.state_manager.update_task(task.id, status=TaskStatus.IN_PROGRESS)
        
        try:
            # Gather context from previous tasks if needed
            context = "Focus on modularity and clear interfaces."
            
            code = await self.coder.write_file(task, context)
            
            # Validate syntax
            is_valid = await self.coder.validate_syntax(task.file_path)
            
            if is_valid:
                logger.info(f"Task {task.id} completed successfully.")
                self.state_manager.update_task(task.id, status=TaskStatus.COMPLETED, file_path=task.file_path)
            else:
                logger.error(f"Task {task.id} syntax validation failed.")
                self.state_manager.update_task(task.id, status=TaskStatus.FAILED, error="Syntax validation failed")
                
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            self.state_manager.update_task(task.id, status=TaskStatus.FAILED, error=str(e))
