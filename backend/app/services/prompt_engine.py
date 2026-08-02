from app.config.prompt_config import SYSTEM_PROMPT


class PromptEngine:

    @staticmethod
    def build(data):

        selected_outputs = "\n".join([f"- {output}" for output in (data.outputs or [])])

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

Selected Outputs:
{selected_outputs}

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
  "story": "string",

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
      "image_prompt": "short search phrase for Pexels or Pixabay",
      "video_prompt": "short search phrase for Pexels or Pixabay",
      "duration": 5,
      "media_type": "image",
      "platform": "Instagram"
    }}

  ]

}}

================================================
SCENE RULES
================================================

If content type is Reel or Shorts

Generate 6-10 scenes.

If content type is Carousel

Generate 3-8 scenes. Each scene must be a carousel card with short on-screen text, a visual search keyword, and an image media suggestion.
For Carousel, use only image scenes and make every `media_type` set to `image`.
Include one short `story` field that summarizes all slides into a single mini-story capturing the sequence and visual narrative.
For Carousel scenes, set `image_prompt` and `keyword` for image search. If `video_prompt` is required, mirror the `image_prompt`.

If the request includes more than one selected output, return a nested JSON structure organized by platform and content type.
Example:
{{
  "instagram": {{
    "carousel": {{ ... }},
    "reel": {{ ... }}
  }},
  "youtube": {{
    "shorts": {{ ... }}
  }}
}}

If only one output is selected, return a flat JSON object with title, hook, description, caption, hashtags, seo_keywords, cta, and scenes.

If content type is YouTube

Generate 15-25 scenes.

Each scene MUST contain

- scene
- text
- keyword
- image_prompt
- video_prompt
- duration
- media_type
- platform

If the selected platform is Instagram, TikTok, or Facebook, keep the scene text short and punchy.
If the selected platform is YouTube, keep the narrative longer and more explanatory.

If package is carousel, focus the output on carousel slide sequencing and concise visual messaging.

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

If the selected content type requires motion, prefer video scenes.
If the selected content type is photo-first, prefer image scenes.

================================================
KEYWORD RULES
================================================

keyword must be suitable for searching stock media on

Pexels
Pixabay
Unsplash

If available, also provide an image_prompt or video_prompt that is a short search phrase for those services.

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

================================================
RELEVANCE RULES
================================================

- Generate exactly one content output.
- Use only the selected platforms and content types.
- Do not introduce extra formats, content items, or unrelated topics.
- If multiple platforms are selected, the response should still be a single piece of content optimized for those selections.
- Do not return arrays of content objects or additional result items.

================================================
OUTPUT
================================================

Use Groq API style metadata for title, description, caption, hashtags, and seo_keywords.

Return ONLY valid JSON.
"""

        return prompt