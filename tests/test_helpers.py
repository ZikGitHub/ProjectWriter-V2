"""
Shared test utilities for the ProjectWriter-V2 test suite.
"""
import asyncio
import httpx
import os
import sys
import time
import warnings
import logging

# Suppress ResourceWarning (e.g. unclosed transport warnings)
warnings.filterwarnings("ignore", category=ResourceWarning)

# Suppress asyncio slow execution logs (warning level)
logging.getLogger("asyncio").setLevel(logging.ERROR)

# Add backend to path so we can import modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def check_ollama_available() -> bool:
    """Synchronously check if Ollama server is reachable."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


def require_ollama(test_case):
    """
    Call inside setUp() or setUpClass() to skip the entire test if Ollama is down.
    Usage:
        def setUp(self):
            require_ollama(self)
    """
    if not check_ollama_available():
        test_case.skipTest(
            f"Ollama is not running at {OLLAMA_BASE_URL}. "
            "Start it with 'ollama serve' then re-run."
        )
