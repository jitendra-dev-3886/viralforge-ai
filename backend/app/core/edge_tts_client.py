import os
import asyncio

import edge_tts


class EdgeTTSClient:

    DEFAULT_VOICE = "en-US-AriaNeural"
    DEFAULT_HINDI_VOICE = "hi-IN-SwaraNeural"

    @classmethod
    async def _generate(
        cls,
        text: str,
        output_file: str,
        voice: str = None,
    ):

        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True,
        )

        selected_voice = voice
        if not selected_voice:
            selected_voice = cls.DEFAULT_HINDI_VOICE if any("\u0900" <= char <= "\u097f" for char in text) else cls.DEFAULT_VOICE

        communicate = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
        )

        await communicate.save(output_file)

        return {
            "path": output_file,
            "size": os.path.getsize(output_file),
        }

    @classmethod
    def generate(
        cls,
        text: str,
        output_file: str,
        voice: str = None,
    ):

        return asyncio.run(
            cls._generate(
                text=text,
                output_file=output_file,
                voice=voice,
            )
        )
