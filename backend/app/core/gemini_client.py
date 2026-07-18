import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

print("GEMINI KEY:", os.getenv("GEMINI_API_KEY")[:10])

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiClient:

    @staticmethod
    def generate(prompt: str):

        print("Calling Gemini...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        print("Gemini response received")

        return response.text