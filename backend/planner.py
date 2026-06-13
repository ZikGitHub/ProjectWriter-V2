import httpx
import os
from typing import List, Dict, Any
from models import ProjectTask, TaskStatus
import json

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
PLANNER_MODEL = "llama3.2:1b"

class Planner:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=60.0)

    async def decompose_request(self, user_request: str) -> List[ProjectTask]:
        prompt = f"""
        You are a senior software architect. Decompose the following user request into small, modular, and testable coding tasks.
        Each task must have a unique ID, a domain (e.g., db, api, ui), a clear description, and list any dependencies (IDs of other tasks it requires).
        
        User Request: {user_request}
        
        Respond ONLY with a JSON list of tasks in the following format:
        [
          {{"id": "task_1", "domain": "db", "description": "Create user schema", "requires": [], "provides": ["user_model"]}},
          {{"id": "task_2", "domain": "api", "description": "Create login endpoint", "requires": ["task_1"], "provides": ["login_api"]}}
        ]
        """
        
        response = await self.client.post("/api/generate", json={
            "model": PLANNER_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        })
        
        if response.status_code == 200:
            result = response.json()
            tasks_data = json.loads(result["response"])
            return [ProjectTask(**task) for task in tasks_data]
        else:
            raise Exception(f"Failed to communicate with Ollama: {response.text}")

    def resolve_dependencies(self, tasks: List[ProjectTask]) -> List[ProjectTask]:
        # Simple topological sort or just return for now as the LLM provides 'requires'
        # In a real scenario, we would validate the DAG here.
        return tasks
