import os
import asyncio

import edge_tts


class EdgeTTSClient:

    DEFAULT_VOICE = "en-US-AriaNeural"

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

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice or cls.DEFAULT_VOICE,
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