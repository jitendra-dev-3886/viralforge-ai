import os
import requests


class OllamaClient:

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_URL",
            "http://127.0.0.1:11434"
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen3:4b"
        )

    def generate(self, prompt: str) -> str:

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "")


ollama_client = OllamaClient()