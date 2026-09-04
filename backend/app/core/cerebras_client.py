import os
from pathlib import Path

from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class CerebrasClient:

    def __init__(self):
        self.client = Cerebras(
            api_key=os.getenv("CEREBRAS_API_KEY")
        )

    def generate(self, prompt: str):

        configured = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
        models = list(dict.fromkeys([configured, "gpt-oss-120b", "gemma-4-31b"]))
        last_error = None
        for model in models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are ViralForge AI."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=int(os.getenv("CEREBRAS_MAX_TOKENS", "1200")),
                )
                self.last_model = model
                return response.choices[0].message.content
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"All configured Cerebras models failed: {last_error}")


cerebras_client = CerebrasClient()
