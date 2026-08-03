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

Return one flat JSON object with title, hook, description, caption, hashtags, seo_keywords, cta, and scenes. The selected platform and content type above are the only format you may create.

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

The selected Content Type controls the delivery format. Package controls creative depth only; never turn a Reel, Shorts, Story, or Long Video into a carousel just because the package is Carousel.

================================================
MEDIA TYPE RULES
================================================

Use `video` for every Reel, Story, Shorts, and Long Video scene. Use `image` for every Carousel, Post, Quote, and Community Post scene. Do not mix the two media types unless the requested format explicitly needs it.

================================================
KEYWORD RULES
================================================

`keyword`, `image_prompt`, and `video_prompt` must be a precise 2-6 word English stock-media search phrase for Pexels or Pixabay. Describe the visible subject, action, and setting (for example: `woman checking budget at desk` or `aerial tropical beach waves`). Do not use abstract concepts, hashtags, text-overlay requests, camera jargon, "viral", "cinematic", "4k", or full sentences.

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

- Create content only for the selected platform and selected content type.
- Make platform conventions part of the result: short opening hook and compact caption for Instagram/Facebook; searchable title and longer explanation for YouTube.
- Do not introduce extra formats, platforms, content items, or unrelated topics.
- Do not return arrays of content objects.

================================================
OUTPUT
================================================

Use Groq API style metadata for title, description, caption, hashtags, and seo_keywords.

Return ONLY valid JSON.
"""

        return prompt
