import asyncio
import os
import sys
import unittest
import time

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from test_helpers import require_ollama
from planner import Planner

class TestPlannerLive(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Use asyncSetUp so skipTest is correctly registered by the async runner."""
        require_ollama(self)
        await asyncio.sleep(1)  # brief pause so Ollama isn't overwhelmed

    async def test_planner_live(self):
        print("\n" + "="*50)
        print("RUNNING LIVE PLANNER TEST (NO MOCKS)")
        print("="*50)
        
        planner = Planner()
        test_request = "Create a simple FastAPI project with one GET endpoint that returns 'Hello World'."
        
        print(f"\n[INPUT] Sending request to Ollama (llama3.2:1b): {test_request}")
        tasks = await planner.decompose_request(test_request)
        
        print(f"\n[OUTPUT] Generated {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  Task {i}: ID={task.id}, Domain={task.domain}, Description={task.description}")
            
        # Assertions
        self.assertGreater(len(tasks), 0)
        for task in tasks:
            self.assertIsNotNone(task.id)
            self.assertIsNotNone(task.domain)
            self.assertIsNotNone(task.description)

if __name__ == '__main__':
    unittest.main()
