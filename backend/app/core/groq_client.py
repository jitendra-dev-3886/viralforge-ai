import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class GroqClient:

    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, prompt: str):

        # The 8B model has a much larger free-tier daily token allowance than
        # the 70B default and is sufficient for structured social content.
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # Free Groq model options include:
        # canopylabs/orpheus-arabic-saudi
        # canopylabs/orpheus-v1-english
        # groq/compound
        # groq/compound-mini
        # llama-3.1-8b-instant
        # llama-3.3-70b-versatile
        # meta-llama/llama-prompt-guard-2-22m
        # meta-llama/llama-prompt-guard-2-86m
        # openai/gpt-oss-120b
        # openai/gpt-oss-20b
        # openai/gpt-oss-safeguard-20b
        # qwen/qwen3.6-27b
        # whisper-large-v3
        # whisper-large-v3-turbo

        response = self.client.chat.completions.create(

            model=model,

            messages=[
                {
                    "role": "system",
                    "content": "You are ViralForge AI."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1200")),
        )

        return response.choices[0].message.content


# Singleton Instance
groq_client = GroqClient()
