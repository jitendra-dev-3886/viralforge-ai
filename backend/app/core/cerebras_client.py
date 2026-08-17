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

        model = os.getenv(
            "CEREBRAS_MODEL",
            "llama-3.3-70b"
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are ViralFlow AI."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=int(
                os.getenv("CEREBRAS_MAX_TOKENS", "1200")
            ),
        )

        return response.choices[0].message.content


cerebras_client = CerebrasClient()