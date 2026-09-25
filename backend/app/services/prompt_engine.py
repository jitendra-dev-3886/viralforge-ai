from app.config.prompt_config import SYSTEM_PROMPT
from app.core.visual_style import get_style


class PromptEngine:
    @staticmethod
    def scene_settings(data):
        """Share scene-count rules between prompts and response validation."""
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
        return scene_count, media_type, script_limit, is_carousel, is_quote

    @staticmethod
    def build(data):
        """Request a complete sequence within the selected scene budget."""
        scene_count, media_type, script_limit, is_carousel, is_quote = PromptEngine.scene_settings(data)
        total_duration = data.total_duration or (scene_count * 5)
        scene_duration = max(2, round(total_duration / scene_count))

        script_limit = max(30, round(total_duration * 2.2)) if media_type == "video" else scene_count * 24
        sequence_rules = (
            "The single scene must deliver a complete, self-contained thought or answer."
            if scene_count == 1 else
            "Plan the entire sequence before writing. The first scene establishes the subject and hook; "
            "the middle scenes advance the same story or explain the essential steps in order; "
            "the final scene resolves the opening and delivers a concrete outcome or takeaway. "
            "For a narrative, include setup, challenge, action and resolution with consistent characters and setting. "
            "For educational or factual content, answer the opening question and include the necessary steps or example. "
            "Every scene must add new information, not repeat a slogan. No cliffhanger, unfinished list, or promised part two. "
            "A CTA is optional and must follow the resolution, never replace it. "
            "Fit the whole arc into the requested count: simplify the scope rather than omit the ending."
        )
        quote_rules = ""
        visual = get_style(data.visual_style)
        visual_direction = f'{visual["name"]}: {visual["description"]}' if visual else "Default"
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
Visual presentation: {visual_direction}. Keep overlay copy concise for this design. Do not put design instructions in stock-media search phrases.
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
  "scenes":[{{"scene":1,"text":"","voice_text":"","keyword":"","image_prompt":"","video_prompt":"","duration":{scene_duration},"media_type":"{media_type}","platform":"{data.platforms[0]}"}}]
}}

Create exactly {scene_count} scenes, numbered consecutively from 1 to {scene_count}.
{sequence_rules}
Each scene text is visible overlay copy: one or two clear sentences of at most {24 if is_carousel else 12} words.
For image slides, the visible text alone must convey the complete sequence; do not hide essential details in the caption or script.
For video, voice_text is the actual spoken narration for that scene, explaining its part of the story in natural complete sentences. Overlay text summarizes that same narration. Aim for approximately two spoken words per second.
For image scenes, set voice_text to the same value as text. Set script to all voice_text values joined in scene order, with no extra events or information. Keep script below {script_limit} words.
Before returning, read the scene sequence alone: does it answer the topic and reach a clear ending? Rewrite it if not.
Set each scene duration close to {scene_duration} seconds so the complete output is approximately {total_duration} seconds.

Every scene must contain every field shown in the schema. keyword, image_prompt, and video_prompt must be a precise 2-6 word English Pexels/Pixabay search phrase that visibly matches the exact scene. Do not use abstract terms, hashtags, text-overlay instructions, camera jargon, or long sentences in those fields.

Set every scene media_type to "{media_type}". Do not create any other platform or content format. For a carousel, set story to all scene text values joined in order, preserving the ending; otherwise story can be empty.
{quote_rules}
""".strip()

    @staticmethod
    def build_json_retry(data):
        """A fresh compact retry when a model returns malformed JSON."""
        return (
            PromptEngine.build(data)
            + "\n\nYour previous response was invalid or had an incomplete scene sequence. Generate a fresh complete response. "
            "It must start with {, end with }, and be valid JSON. Keep exactly the requested scene count. "
            "Use short sentences and at most 3 words per search phrase. Preserve every essential story beat and the ending. "
            "Keep description and caption to one sentence each. Keep script aligned with the scene narration and story aligned with the slides, "
            "and use at most 3 hashtags and 3 SEO keywords. Finish the entire JSON object."
        )
