"""
Minimal test runner for a local quantized GGML model using llama-cpp-python.

Usage:
  - Place your model file in C:\models\ (example: ggml-vicuna-7b-q4_0.bin)
  - Set the MODEL_PATH environment variable or edit the default below
  - Create and activate a virtualenv and install `llama-cpp-python`
    pip install llama-cpp-python
  - Run: python test_llama.py

This script is intentionally minimal and binds only to local files.
"""

import os
from pathlib import Path
from llama_cpp import Llama


MODEL_PATH = os.environ.get("MODEL_PATH", r"C:\models\ggml-vicuna-7b-q4_0.bin")


def main():
    model_file = Path(MODEL_PATH)
    if not model_file.exists():
        print(f"Model not found at {model_file}. Please download a quantized ggml model and set MODEL_PATH.")
        return

    print(f"Loading model from {model_file} ...")

    llm = Llama(model_path=str(model_file))

    prompt = "Write 5 concise Instagram carousel captions about AI safety."

    print("Generating...")

    resp = llm.create(prompt=prompt, max_tokens=200)

    text = resp.get("choices", [{}])[0].get("text") or resp.get("output") or resp

    print("\n=== RESULT ===\n")
    print(text)


if __name__ == "__main__":
    main()
