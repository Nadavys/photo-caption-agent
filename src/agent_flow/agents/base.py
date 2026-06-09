import os

from dotenv import load_dotenv
from ollama import Client

from agent_flow.config import DEFAULT_MODEL

load_dotenv()


class BaseAgent:
    def __init__(self) -> None:
        host = os.environ.get("OLLAMA_HOST")
        api_key = os.environ.get("OLLAMA_API_KEY")
        if not host:
            raise ValueError("OLLAMA_HOST environment variable is not set.")
        self._model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self._temperature = float(os.environ.get("OLLAMA_TEMPERATURE", "1.0"))
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = Client(host=host, headers=headers)
