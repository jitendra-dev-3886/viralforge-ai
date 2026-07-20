from app.config.prompt_config import SYSTEM_PROMPT


class PromptEngine:

    @staticmethod
    def build(data):

        prompt = f"""
{SYSTEM_PROMPT}

================================================
CONTENT GENERATION REQUEST
================================================

Platforms:
{", ".join(data.platforms)}

Content Types:
{", ".join(data.content_types)}

Niche:
{data.niche}

Topic:
{data.topic}

Package:
{data.package}

================================================
IMPORTANT
================================================

Return ONLY valid JSON.

DO NOT:

- use markdown
- use ```json
- write explanations
- write comments
- return invalid JSON

JSON must start with {{
and end with }}

================================================
RETURN THIS EXACT JSON SCHEMA
================================================

{{
  "title": "string",

  "hook": "string",

  "description": "string",

  "caption": "string",

  "hashtags": [
    "#tag1",
    "#tag2"
  ],

  "cta": "string",

  "seo_keywords": [
    "keyword1",
    "keyword2"
  ],

  "scenes": [

    {{
      "scene": 1,
      "text": "Scene narration",
      "keyword": "pexels search keyword",
      "duration": 5,
      "media_type": "image"
    }}

  ]

}}

================================================
SCENE RULES
================================================

If content type is Reel or Shorts

Generate 6-10 scenes.

If content type is Carousel

Generate 7-10 scenes.

If content type is YouTube

Generate 15-25 scenes.

Each scene MUST contain

- scene
- text
- keyword
- duration
- media_type

================================================
MEDIA TYPE RULES
================================================

Use

image

for quotes,
finance,
motivation,
psychology,
business

Use

video

for

travel,
sports,
nature,
animals,
food,
fitness,
cinematic

================================================
KEYWORD RULES
================================================

keyword must be suitable for searching stock media on

Pexels
Pixabay
Unsplash

Do NOT use long sentences.

Good examples:

saving money

business meeting

space galaxy

healthy food

forest river

================================================
OUTPUT
================================================

Return ONLY valid JSON.
"""

        return prompt