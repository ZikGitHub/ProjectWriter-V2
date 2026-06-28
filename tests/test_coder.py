import asyncio
import os
import sys
import shutil
import unittest
import time

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from test_helpers import require_ollama
from coder import Coder
from models import ProjectTask, TaskStatus

class TestCoderLive(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Use asyncSetUp so skipTest is correctly registered by the async runner."""
        require_ollama(self)
        await asyncio.sleep(1)  # brief pause so Ollama isn't overwhelmed
        self.test_dir = "./test_coder_live_workspace"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        self.coder = Coder(state_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    async def test_coder_live_and_validate(self):
        print("\n" + "="*50)
        print("RUNNING LIVE CODER TEST (NO MOCKS)")
        print("="*50)
        
        task = ProjectTask(
            id="task_live_1",
            domain="db",
            description="Write a python function get_db_connection() that returns 'sqlite_conn' string.",
            file_path="db/task_live_1.py"
        )
        
        print(f"\n[INPUT] Sending task description to Ollama (qwen2.5-coder:1.5b): {task.description}")
        code = await self.coder.write_file(task, "No context")
        
        print("\n[OUTPUT] Generated Code:")
        print(code)
        
        # Verify file written
        expected_path = os.path.join(self.test_dir, task.file_path)
        self.assertTrue(os.path.exists(expected_path))
        
        # Validate syntax
        is_valid = await self.coder.validate_syntax(task.file_path)
        print(f"Syntax validation passed: {is_valid}")
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()
