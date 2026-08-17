import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class OpenRouterClient:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    def generate(self, prompt: str):

        model = os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-4o"
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
                os.getenv("OPENROUTER_MAX_TOKENS", "1200")
            ),
        )

        return response.choices[0].message.content


# Singleton Instance
openrouter_client = OpenRouterClient()