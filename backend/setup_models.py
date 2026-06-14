import os
import httpx
import asyncio

from logger_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

async def pull_models():
    models = ["llama3.2:1b", "qwen2.5-coder:1.5b"]
    async with httpx.AsyncClient(timeout=600.0) as client:
        for model in models:
            logger.info(f"Pulling model: {model}...")
            try:
                response = await client.post(f"{OLLAMA_BASE_URL}/api/pull", json={"name": model}, timeout=None)
                logger.info(f"Successfully pulled {model}")
            except Exception as e:
                logger.error(f"Failed to pull {model}: {e}")

if __name__ == "__main__":
    asyncio.run(pull_models())
