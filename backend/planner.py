import httpx
import os
from typing import List, Dict, Any
from models import ProjectTask, TaskStatus
from logger_config import get_logger
import json

logger = get_logger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
PLANNER_MODEL = "llama3.2:1b"

class Planner:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=60.0)
        logger.info(f"Planner initialized using model {PLANNER_MODEL}")

    async def decompose_request(self, user_request: str) -> List[ProjectTask]:
        logger.info(f"Decomposing request: {user_request[:50]}...")
        prompt = f"""
        You are a senior software architect. Decompose the following user request into small, modular, and testable coding tasks.
        Each task must have a unique ID, a domain (e.g., db, api, ui), a clear description, and list any dependencies (IDs of other tasks it requires).
        
        User Request: {user_request}
        
        IMPORTANT: Do NOT simply repeat the example tasks below. Analyze the User Request carefully and provide a tailored plan.
        
        Respond ONLY with a JSON list of tasks in the following format:
        [
          {{"id": "task_1", "domain": "db", "description": "Create specific database schema for this request", "requires": [], "provides": ["model_name"]}},
          {{"id": "task_2", "domain": "api", "description": "Create specific endpoint related to the request", "requires": ["task_1"], "provides": ["api_name"]}}
        ]
        """
        
        try:
            response = await self.client.post("/api/generate", json={
                "model": PLANNER_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            })
            
            if response.status_code == 200:
                result = response.json()
                tasks_data = json.loads(result["response"])
                
                # Handle different JSON formats from LLM
                if isinstance(tasks_data, dict) and "tasks" in tasks_data:
                    tasks_data = tasks_data["tasks"]
                
                if not isinstance(tasks_data, list):
                    logger.error(f"Unexpected JSON format from Planner: {tasks_data}")
                    raise Exception(f"Unexpected JSON format from Planner: {tasks_data}")

                logger.info(f"Successfully decomposed request into {len(tasks_data)} tasks.")
                return [ProjectTask(**task) for task in tasks_data]
            else:
                logger.error(f"Failed to communicate with Ollama: {response.text}")
                raise Exception(f"Failed to communicate with Ollama: {response.text}")
        except Exception as e:
            logger.error(f"Exception during request decomposition: {str(e)}")
            raise

    def resolve_dependencies(self, tasks: List[ProjectTask]) -> List[ProjectTask]:
        # Simple topological sort or just return for now as the LLM provides 'requires'
        # In a real scenario, we would validate the DAG here.
        return tasks
