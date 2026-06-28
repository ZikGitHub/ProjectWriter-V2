import asyncio
import os
import sys
import shutil
import unittest
import time

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from test_helpers import require_ollama
from orchestrator_v2 import Orchestrator
from state_manager import StateManager
from models import ProjectState, ProjectTask, TaskStatus
from langgraph.graph import END

class TestOrchestratorLive(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Use asyncSetUp so skipTest is correctly registered by the async runner."""
        require_ollama(self)
        await asyncio.sleep(2)  # give Ollama breathing room between test runs
        self.test_dir = "./test_orchestrator_live_workspace"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        self.state_manager = StateManager(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    async def test_orchestrator_live_workflow(self):
        print("\n" + "="*50)
        print("RUNNING LIVE ORCHESTRATOR V2 LANGGRAPH WORKFLOW (NO MOCKS)")
        print("="*50)
        
        project_id = self.state_manager.set_project("live_orchestrator_project")
        orchestrator = Orchestrator(self.state_manager)
        
        # Two independent tasks (no dependency chain) so both can execute
        # regardless of whether the other fails
        task_1 = ProjectTask(
            id="task_1",
            domain="db",
            description="Write a python function get_db_name() that returns string 'live_db'.",
            requires=[]
        )
        task_2 = ProjectTask(
            id="task_2",
            domain="api",
            description="Write a python function get_api_endpoint() that returns string '/endpoint'.",
            requires=[]  # No dependency - runs independently
        )
        
        state = self.state_manager.load_state()
        state.tasks = [task_1, task_2]
        self.state_manager.save_state()
        
        print("\n[PROCESS] Running execution loop...")
        await orchestrator.run_execution_loop()
        
        # Verify both tasks were executed (no longer PENDING)
        final_state = self.state_manager.load_state()
        print("\n[OUTPUT] Final task status:")
        for t in final_state.tasks:
            print(f"  Task {t.id}: Status={t.status.value}, File={t.file_path}, Error={t.error}")
            
        # Both tasks had no dependencies, so both must have been attempted
        self.assertNotEqual(final_state.tasks[0].status, TaskStatus.PENDING,
                            f"Task {final_state.tasks[0].id} was never executed!")
        self.assertNotEqual(final_state.tasks[1].status, TaskStatus.PENDING,
                            f"Task {final_state.tasks[1].id} was never executed!")
        
        # If task completed, verify the file was written
        for t in final_state.tasks:
            if t.status == TaskStatus.COMPLETED:
                full_path = os.path.join(self.state_manager.state_dir, t.file_path)
                self.assertTrue(os.path.exists(full_path), f"File not found for task {t.id}")
                print(f"  --> File exists at: {full_path}")

if __name__ == '__main__':
    unittest.main()
