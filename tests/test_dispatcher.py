import unittest
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from dispatcher import dispatcher_node
from models import ProjectState, ProjectTask, TaskStatus, TaskState

class TestDispatcherNode(unittest.TestCase):
    def test_dispatcher_node_identifies_ready_tasks(self):
        # Arrange: task_1 has no dependencies (ready), task_2 depends on task_1 (not ready)
        task_1 = ProjectTask(
            id="task_1",
            domain="db",
            description="Create database schema",
            requires=[],
            status=TaskStatus.PENDING
        )
        task_2 = ProjectTask(
            id="task_2",
            domain="api",
            description="Create API endpoints",
            requires=["task_1"],
            status=TaskStatus.PENDING
        )
        
        state = ProjectState(
            project_name="Test Dispatcher",
            tasks=[task_1, task_2],
            completed_files=[]
        )
        
        # Act
        result = dispatcher_node(state)
        
        # Assert
        self.assertIn("next", result)
        sends = result["next"]
        self.assertEqual(len(sends), 1)
        
        # Verify Send targeting execute_node for task_1
        send = sends[0]
        self.assertEqual(send.node, "execute_node")
        self.assertEqual(send.arg["id"], "task_1")
        self.assertEqual(send.arg["file_path"], "db/task_1.py")
        self.assertEqual(send.arg["instruction"], "Create database schema")

    def test_dispatcher_node_respects_completed_dependencies(self):
        # Arrange: task_1 is completed, task_2 depends on task_1 (now ready)
        task_1 = ProjectTask(
            id="task_1",
            domain="db",
            description="Create database schema",
            requires=[],
            status=TaskStatus.COMPLETED,
            file_path="db/task_1.py"
        )
        task_2 = ProjectTask(
            id="task_2",
            domain="api",
            description="Create API endpoints",
            requires=["task_1"],
            status=TaskStatus.PENDING
        )
        
        state = ProjectState(
            project_name="Test Dispatcher 2",
            tasks=[task_1, task_2],
            completed_files=["task_1"]
        )
        
        # Act
        result = dispatcher_node(state)
        
        # Assert
        self.assertIn("next", result)
        sends = result["next"]
        self.assertEqual(len(sends), 1)
        
        # Verify Send targeting execute_node for task_2
        send = sends[0]
        self.assertEqual(send.node, "execute_node")
        self.assertEqual(send.arg["id"], "task_2")
        self.assertEqual(send.arg["file_path"], "api/task_2.py")

if __name__ == '__main__':
    unittest.main()
