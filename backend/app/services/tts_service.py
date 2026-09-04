import os
import uuid
import edge_tts


class TTSService:

    VOICE = "en-US-AndrewNeural"

    @staticmethod
    async def generate(text: str, output_dir: str):

        os.makedirs(output_dir, exist_ok=True)

        filename = f"{uuid.uuid4()}.mp3"

        output_file = os.path.join(output_dir, filename)

        voice = "hi-IN-SwaraNeural" if any("\u0900" <= char <= "\u097f" for char in text) else TTSService.VOICE
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice
        )

        await communicate.save(output_file)

        return output_file
