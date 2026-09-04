import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Groq Client
# ---------------------------------------------------------

class GroqClient:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

        self.client = Groq(api_key=self.api_key)

        # FREE models for now.
        # Later, simply change GROQ_MODELS in .env.
        self.models = self._load_models()

        self.max_tokens = max(3000, int(os.getenv("GROQ_MAX_TOKENS", "3000")))

        self.temperature = float(
            os.getenv("GROQ_TEMPERATURE", "0.7")
        )

    # -----------------------------------------------------
    # Load models
    # -----------------------------------------------------

    def _load_models(self):
        models = os.getenv(
            "GROQ_MODELS",
            "openai/gpt-oss-20b,qwen/qwen3.6-27b,groq/compound-mini"
        )

        configured = [
            model.strip()
            for model in models.split(",")
            if model.strip()
        ]
        fallbacks = ["openai/gpt-oss-20b", "qwen/qwen3.6-27b", "groq/compound-mini"]
        return list(dict.fromkeys(configured + fallbacks))

    # -----------------------------------------------------
    # Generate
    # -----------------------------------------------------

    def generate(self, prompt: str, json_mode: bool = False):

        last_error = None

        for model in self.models:

            try:

                print(f"[Groq] Trying model: {model}")

                request = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are ViralForge AI. Return valid JSON only."
                                if json_mode else "You are ViralForge AI."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }

                if json_mode:
                    request["response_format"] = {"type": "json_object"}

                try:
                    response = self.client.chat.completions.create(**request)
                except Exception:
                    # Some otherwise usable Groq models do not expose JSON
                    # mode. Fall back to their regular response and let the
                    # service parser validate it before accepting the result.
                    if not json_mode:
                        raise
                    request.pop("response_format", None)
                    response = self.client.chat.completions.create(**request)

                content = response.choices[0].message.content

                if content:
                    self.last_model = model
                    print(f"[Groq] Success: {model}")
                    return content

            except Exception as e:

                last_error = e

                print(
                    f"[Groq] Failed: {model} -> {e}"
                )

                # Try the next model
                continue

        # All models failed
        raise RuntimeError(
            f"All configured Groq models failed: {last_error}"
        )


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

groq_client = GroqClient()
