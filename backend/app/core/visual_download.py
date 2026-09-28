"""Shared per-file limit for fetched images and video clips."""
import os

import requests


MAX_VISUAL_BYTES = 10_000_000


class VisualSizeLimitError(ValueError):
    def __init__(self):
        super().__init__("Visual exceeds the 10 MB per-file limit")


def limited_chunks(response):
    try:
        size = int(response.headers.get("Content-Length", 0))
    except (TypeError, ValueError):
        size = 0
    if size > MAX_VISUAL_BYTES:
        raise VisualSizeLimitError()
    total = 0
    for chunk in response.iter_content(65536):
        if chunk:
            total += len(chunk)
            if total > MAX_VISUAL_BYTES:
                raise VisualSizeLimitError()
            yield chunk


def download_visual(url, save_path):
    partial = str(save_path) + ".part"
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(partial, "wb") as output:
                for chunk in limited_chunks(response):
                    output.write(chunk)
        os.replace(partial, save_path)
    finally:
        if os.path.exists(partial):
            os.remove(partial)
    return {"file_path": save_path, "file_size": os.path.getsize(save_path)}
