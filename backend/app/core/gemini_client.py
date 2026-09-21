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
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config={"response_mime_type": "application/json", "max_output_tokens": int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))},
        )

        logger.info("Gemini response received")

        return response.text
