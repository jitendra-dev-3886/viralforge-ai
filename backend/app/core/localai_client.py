import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class LocalAIClient:

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("LOCALAI_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("LOCALAI_API_KEY")

    def generate(self, prompt: str, model: str = None):
        """Call a LocalAI (OpenAI-compatible) chat/completions endpoint and return text."""

        url = f"{self.base_url.rstrip('/')}/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = [
            {"role": "system", "content": "You are ViralForge AI."},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": model or os.getenv("LOCALAI_MODEL", "ggml-vicuna-7b-q4_0"),
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        # Support different response shapes (OpenAI-like)
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            # Fallback: some LocalAI builds return 'output' or 'text'
            if isinstance(data, dict):
                if "output" in data:
                    return data["output"]
                if "text" in data:
                    return data["text"]

            raise


# Singleton
localai_client = LocalAIClient()
