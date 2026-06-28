import unittest
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from reducer import reducer_node
from models import ProjectState, ProjectTask, TaskStatus, TaskState

class TestReducerNode(unittest.TestCase):
    def test_reducer_node_processes_successful_updates(self):
        # Arrange
        task_1 = ProjectTask(
            id="task_1",
            domain="db",
            description="Create database schema",
            status=TaskStatus.IN_PROGRESS
        )
        state = ProjectState(
            project_name="Test Reducer",
            tasks=[task_1],
            completed_files=[]
        )
        
        # Simulated updates returned from execute_node branches
        updates = [
            {
                "id": "task_1",
                "file_path": "db/task_1.py",
                "instruction": "Create database schema",
                "target_model": "qwen2.5-coder:1.5b",
                "current_code": "print('DB code')"
            }
        ]
        
        # Act
        result = reducer_node(state, updates=updates)
        
        # Assert
        # reducer_node returns dictionary of fields to update in the state
        self.assertIn("completed_files", result)
        self.assertIn("task_1", result["completed_files"])
        self.assertEqual(result["updates"], [])  # Clears updates channel
        
        # Task itself is updated in-place in state.tasks
        self.assertEqual(task_1.status, TaskStatus.COMPLETED)
        self.assertEqual(task_1.file_path, "db/task_1.py")

    def test_reducer_node_processes_failed_updates(self):
        # Arrange
        task_1 = ProjectTask(
            id="task_1",
            domain="db",
            description="Create database schema",
            status=TaskStatus.IN_PROGRESS
        )
        state = ProjectState(
            project_name="Test Reducer Fail",
            tasks=[task_1],
            completed_files=[]
        )
        
        # Simulated updates indicating a failure (current_code is None or missing)
        updates = [
            {
                "id": "task_1",
                "file_path": "db/task_1.py",
                "instruction": "Create database schema",
                "target_model": "qwen2.5-coder:1.5b",
                "current_code": None
            }
        ]
        
        # Act
        result = reducer_node(state, updates=updates)
        
        # Assert
        self.assertNotIn("task_1", result.get("completed_files", []))
        self.assertEqual(result["updates"], [])
        
        self.assertEqual(task_1.status, TaskStatus.FAILED)
        self.assertIn("failed", task_1.error.lower())

if __name__ == '__main__':
    unittest.main()
