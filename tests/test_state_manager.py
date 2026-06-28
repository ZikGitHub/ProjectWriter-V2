import unittest
import sys
import os
import shutil

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from state_manager import StateManager
from models import ProjectTask, TaskStatus

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_state_manager_workspace"
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

    def test_set_project(self):
        # Act
        project_id = self.state_manager.set_project("My Cool Project")
        
        # Assert
        self.assertTrue(project_id.startswith("my_cool_project_"))
        self.assertEqual(self.state_manager.state.project_name, "My Cool Project")
        self.assertTrue(os.path.exists(self.state_manager.state_path))

    def test_load_state_non_existent(self):
        # Act: state file doesn't exist yet, should create a default state
        state = self.state_manager.load_state()
        
        # Assert
        self.assertEqual(state.project_name, "New Project")
        self.assertTrue(os.path.exists(self.state_manager.state_path))

    def test_save_and_load_state(self):
        # Arrange
        self.state_manager.set_project("Persisted Project")
        self.state_manager.state.version = "1.2.3"
        task = ProjectTask(id="t1", domain="db", description="test task")
        self.state_manager.state.tasks.append(task)
        
        # Act
        self.state_manager.save_state()
        
        # Load in a fresh manager pointing to the same place
        new_manager = StateManager(base_dir=self.test_dir)
        new_manager.state_dir = self.state_manager.state_dir
        new_manager.state_path = self.state_manager.state_path
        loaded_state = new_manager.load_state()
        
        # Assert
        self.assertEqual(loaded_state.project_name, "Persisted Project")
        self.assertEqual(loaded_state.version, "1.2.3")
        self.assertEqual(len(loaded_state.tasks), 1)
        self.assertEqual(loaded_state.tasks[0].id, "t1")

    def test_update_task(self):
        # Arrange
        self.state_manager.set_project("Task Update Project")
        task = ProjectTask(id="task_x", domain="ui", description="UI mockup", status=TaskStatus.PENDING)
        self.state_manager.add_task(task)
        
        # Act
        self.state_manager.update_task("task_x", status=TaskStatus.COMPLETED, file_path="ui/mockup.py")
        
        # Assert
        updated_state = self.state_manager.load_state()
        updated_task = updated_state.tasks[0]
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        self.assertEqual(updated_task.file_path, "ui/mockup.py")

if __name__ == '__main__':
    unittest.main()
