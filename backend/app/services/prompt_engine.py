from app.config.prompt_config import SYSTEM_PROMPT


class PromptEngine:
    @staticmethod
    def build(data):
        """Create a compact prompt so model output is not truncated mid-JSON."""
        content_type = " ".join(data.content_types).lower()
        is_carousel = "carousel" in content_type
        is_quote = "quote" in content_type or (data.package.lower() == "quote" and not is_carousel)
        if is_carousel:
            scene_count, media_type, script_limit = 6, "image", 120
        elif is_quote:
            scene_count, media_type, script_limit = 1, "image", 30
        elif any(value in content_type for value in ("reel", "short", "story")):
            scene_count, media_type, script_limit = 7, "video", 120
        elif "long video" in content_type or content_type.strip() == "video":
            scene_count, media_type, script_limit = 10, "video", 260
        else:
            scene_count, media_type, script_limit = 5, "image", 120

        if data.scene_count is not None and not is_quote:
            scene_count = max(3, data.scene_count) if is_carousel else data.scene_count
        total_duration = data.total_duration or (scene_count * 5)
        scene_duration = max(2, round(total_duration / scene_count))

        quote_rules = ""
        if is_quote:
            quote_rules = (
                f"QUOTE RULES: Generate exactly one original two-line {data.language} quote. "
                "The scenes[0].text value must contain exactly two short lines separated by "
                "the JSON newline escape \\n. Do not add an author name. Use natural Devanagari "
                "for Hindi and do not transliterate Hindi into Latin letters. Put the same "
                "two-line quote in script."
            )

        return f"""
{SYSTEM_PROMPT}

Create one {", ".join(data.content_types)} for {", ".join(data.platforms)}.
Niche: {data.niche}
Topic: {data.topic}
Package: {data.package}
Language: {data.language}
Style or tone: {data.style or "Engaging"}
Target total duration: {total_duration} seconds

Return ONLY one valid JSON object. Do not use Markdown, comments, code fences, or text before or after the JSON. Use normal JSON double quotes. Never include an unescaped double quote inside a string.

Use this exact top-level shape:
{{
  "title":"",
  "hook":"",
  "description":"",
  "script":"",
  "caption":"",
  "story":"",
  "hashtags":["#tag"],
  "seo_keywords":["keyword"],
  "cta":"",
  "scenes":[{{"scene":1,"text":"","keyword":"","image_prompt":"","video_prompt":"","duration":{scene_duration},"media_type":"{media_type}","platform":"{data.platforms[0]}"}}]
}}

Create exactly {scene_count} scenes. Each scene text is visible overlay copy: one clear sentence of at most 12 words. Scenes must form a connected sequence: hook, value, payoff, CTA. Keep script below {script_limit} words.
Set each scene duration close to {scene_duration} seconds so the complete output is approximately {total_duration} seconds.

Every scene must contain every field shown in the schema. keyword, image_prompt, and video_prompt must be a precise 2-6 word English Pexels/Pixabay search phrase that visibly matches the exact scene. Do not use abstract terms, hashtags, text-overlay instructions, camera jargon, or long sentences in those fields.

Set every scene media_type to "{media_type}". Do not create any other platform or content format. For a carousel, write a short story; otherwise story can be empty.
{quote_rules}
""".strip()

    @staticmethod
    def build_json_retry(data):
        """A fresh compact retry when a model returns malformed JSON."""
        return (
            PromptEngine.build(data)
            + "\n\nYour previous response could not be parsed. Generate a fresh, shorter response. "
            "It must start with {, end with }, and be valid JSON."
        )
