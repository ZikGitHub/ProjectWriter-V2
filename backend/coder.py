import httpx
import os
import asyncio
from typing import List, Dict, Any
from models import ProjectTask, TaskStatus, ProjectState
import json

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CODER_MODEL = "qwen2.5-coder:1.5b"

class Coder:
    def __init__(self, state_dir: str = "./generated_project"):
        self.client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=120.0)
        self.state_dir = state_dir

    async def write_file(self, task: ProjectTask, context: str) -> str:
        prompt = f"""
        You are an expert software engineer. Your task is to write high-quality, production-ready Python code for the following task.
        
        Task Description: {task.description}
        Domain: {task.domain}
        Context (Previous tasks/contracts): {context}
        
        Respond ONLY with the complete Python source code. Do not include markdown blocks or explanations.
        """
        
        response = await self.client.post("/api/generate", json={
            "model": CODER_MODEL,
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            code = response.json()["response"].strip()
            
            # Robust code extraction
            import re
            code_block_match = re.search(r"```(?:\w+)?\n(.*?)\n```", code, re.DOTALL)
            if code_block_match:
                code = code_block_match.group(1).strip()
            else:
                # Fallback: if no blocks but has backticks, try to strip them
                code = code.replace("```", "").strip()
            
            # Determine file path if not provided
            if not task.file_path:
                task.file_path = f"{task.domain}/{task.id}.py" # Default naming convention
            
            full_path = os.path.join(self.state_dir, task.file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w") as f:
                f.write(code)
            
            return code
        else:
            raise Exception(f"Failed to generate code: {response.text}")

    async def validate_syntax(self, file_path: str) -> bool:
        full_path = os.path.join(self.state_dir, file_path)
        try:
            with open(full_path, "r") as f:
                source = f.read()
            compile(source, full_path, 'exec')
            return True
        except Exception:
            return False
