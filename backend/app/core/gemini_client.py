import logging
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiClient:

    @staticmethod
    def generate(prompt: str):

        logger.info("Calling Gemini")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        logger.info("Gemini response received")

        return response.text
