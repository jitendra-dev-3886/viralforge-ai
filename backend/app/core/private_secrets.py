"""Persistent server-only secrets, outside the publicly served storage folder."""
import os
from pathlib import Path
from cryptography.fernet import Fernet


def private_secret(name, env_name):
    configured = os.getenv(env_name)
    if configured:
        return configured.encode()
    folder = Path(__file__).resolve().parents[2] / ".secrets"
    folder.mkdir(mode=0o700, exist_ok=True)
    path = folder / name
    if not path.exists():
        try:
            with path.open("xb") as file:
                file.write(Fernet.generate_key())
            path.chmod(0o600)
        except FileExistsError:
            pass
    return path.read_bytes().strip()
