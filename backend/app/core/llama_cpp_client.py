import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class LlamaCppClient:

    _llm = None
    _model_path = None

    @classmethod
    def get_model_path(cls):
        model_path = os.getenv("LLAMA_CPP_MODEL_PATH", r"C:\models\ggml-vicuna-7b-q4_0.bin")
        if not Path(model_path).exists():
            raise Exception(
                f"LLAMA_CPP_MODEL_PATH not found or file does not exist: {model_path}"
            )
        return model_path

    @classmethod
    def get_llm(cls):
        model_path = cls.get_model_path()
        if cls._llm is None or cls._model_path != model_path:
            try:
                from llama_cpp import Llama
            except ImportError as exc:
                raise Exception(
                    "llama-cpp-python is not installed. Install it with `pip install llama-cpp-python`."
                ) from exc

            cls._llm = Llama(model_path=model_path)
            cls._model_path = model_path

        return cls._llm

    @classmethod
    def generate(cls, prompt: str, max_tokens: int = 2000, temperature: float = 0.7):
        llm = cls.get_llm()
        response = llm.create(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if isinstance(response, dict):
            choice = response.get("choices", [{}])[0]
            text = choice.get("text") or choice.get("message", {}).get("content")
            if text:
                return text
            if "output" in response:
                return response["output"]

        raise Exception("Unexpected llama-cpp response format.")


llama_cpp_client = LlamaCppClient()
