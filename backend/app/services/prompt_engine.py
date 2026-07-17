from app.config.prompt_config import SYSTEM_PROMPT


class PromptEngine:

    @staticmethod
    def build(data):

        prompt = f"""
{SYSTEM_PROMPT}

================================================

PLATFORMS

{", ".join(data.platforms)}

================================================

CONTENT TYPES

{", ".join(data.content_types)}

================================================

NICHE

{data.niche}

================================================

TOPIC

{data.topic}

================================================

PACKAGE

{data.package}

================================================

Generate only requested content.

Return valid JSON only.

"""

        return prompt