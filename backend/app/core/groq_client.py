import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class GroqClient:

    @staticmethod
    def generate(prompt: str) -> str:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,

        )

        return response.choices[0].message.content