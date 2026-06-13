import os
import httpx
import asyncio

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

async def pull_models():
    models = ["llama3.2:1b", "qwen2.5-coder:1.5b"]
    async with httpx.AsyncClient(timeout=600.0) as client:
        for model in models:
            print(f"Pulling model: {model}...")
            try:
                response = await client.post(f"{OLLAMA_BASE_URL}/api/pull", json={"name": model}, timeout=None)
                print(f"Successfully pulled {model}")
            except Exception as e:
                print(f"Failed to pull {model}: {e}")

if __name__ == "__main__":
    asyncio.run(pull_models())
