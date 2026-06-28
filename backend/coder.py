import httpx
import os
import asyncio
from typing import List, Dict, Any
from models import ProjectTask, TaskStatus, ProjectState
from logger_config import get_logger
import json

logger = get_logger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CODER_MODEL = "qwen2.5-coder:1.5b"

class Coder:
    def __init__(self, state_dir: str = "./generated_project"):
        self.client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=None)
        self.state_dir = state_dir
        logger.info(f"Coder initialized with state_dir: {state_dir} and model: {CODER_MODEL}")

    async def write_file(self, task: ProjectTask, context: str, state_dir: str = None) -> str:
        current_state_dir = state_dir or self.state_dir
        logger.info(f"Generating code for task: {task.id} in {current_state_dir}")
        prompt = f"""
        You are an expert software engineer. Your task is to write high-quality, production-ready Python code for the following task.
        
        Task Description: {task.description}
        Domain: {task.domain}
        Context (Previous tasks/contracts): {context}
        
        Respond ONLY with the complete Python source code. Do not include markdown blocks or explanations.
        """
        
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Attempt {attempt} of {max_retries} to generate code for task {task.id}...")
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
                    
                    full_path = os.path.join(current_state_dir, task.file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    with open(full_path, "w") as f:
                        f.write(code)
                    
                    logger.info(f"Code written to {full_path}")
                    return code
                else:
                    logger.error(f"Failed to generate code for task {task.id}: {response.text}")
                    raise Exception(f"Failed to generate code: {response.text}")
            except Exception as e:
                logger.error(f"Exception during code generation for task {task.id} (attempt {attempt}): {str(e)}")
                if attempt < max_retries:
                    wait = 2 ** attempt  # exponential backoff: 2s, 4s
                    logger.info(f"Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise

    async def validate_syntax(self, file_path: str, state_dir: str = None) -> bool:
        current_state_dir = state_dir or self.state_dir
        logger.info(f"Validating syntax for {file_path} in {current_state_dir}")
        full_path = os.path.join(current_state_dir, file_path)
        try:
            with open(full_path, "r") as f:
                source = f.read()
            compile(source, full_path, 'exec')
            logger.info(f"Syntax validation passed for {file_path}")
            return True
        except Exception as e:
            logger.warning(f"Syntax validation failed for {file_path}: {str(e)}")
            return False
