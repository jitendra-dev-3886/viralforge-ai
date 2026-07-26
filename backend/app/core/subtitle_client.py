import os


class SubtitleClient:

    @staticmethod
    def seconds_to_timestamp(seconds: float) -> str:

        milliseconds = int((seconds % 1) * 1000)

        total_seconds = int(seconds)

        hours = total_seconds // 3600

        minutes = (total_seconds % 3600) // 60

        secs = total_seconds % 60

        return (
            f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
        )

    @staticmethod
    def generate_srt(
        text: str,
        duration: int,
        output_path: str,
    ):

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        # Split text into small readable subtitle lines
        words = text.split()

        lines = []

        chunk = []

        for word in words:

            chunk.append(word)

            if len(chunk) >= 6:
                lines.append(" ".join(chunk))
                chunk = []

        if chunk:
            lines.append(" ".join(chunk))

        total_lines = len(lines)

        line_duration = duration / max(total_lines, 1)

        current = 0.0

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            for index, line in enumerate(lines, start=1):

                start = SubtitleClient.seconds_to_timestamp(current)

                end = SubtitleClient.seconds_to_timestamp(
                    current + line_duration
                )

                file.write(f"{index}\n")

                file.write(f"{start} --> {end}\n")

                file.write(f"{line}\n\n")

                current += line_duration

        return output_path