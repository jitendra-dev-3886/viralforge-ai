VISUAL_NICHE_BOUNDARIES = {
    "FinLogic": "saving, debt, EMI, investing, SIP, compounding, budgeting, emergency funds, insurance, taxes, credit score, cash flow, assets/liabilities, lifestyle inflation, spending psychology, wealth building, retirement, passive income, risk management",
    "ZenHack": "mindset, habits, discipline, focus, confidence, overthinking, stress, clarity, productivity, procrastination, self-control, resilience, motivation, fear, failure, decision-making, personal growth, self-awareness, identity change",
    "PsychoPath.cc": "psychology, behavior, emotions, cognition, biases, body language, attachment, emotional suppression, manipulation, personality, social behavior, trauma responses, perception, memory, subconscious behavior, triggers, emotional intelligence",
    "Intimacy Index": "love, relationships, communication, trust, emotional availability, attachment, compatibility, boundaries, conflict, intimacy, toxic patterns, respect, loyalty, love languages, dating, commitment, vulnerability, breakup recovery",
    "Cosmic Night": "planets, stars, black holes, neutron stars, pulsars, supernovae, galaxies, nebulae, exoplanets, gravity, space-time, dark matter, dark energy, cosmic collisions, space missions, universe scale, cosmic mysteries",
    "YS Tech": "AI, AI agents, automation, machine learning, APIs, coding, debugging, databases, cloud, system design, architecture, DevOps, CI/CD, cybersecurity, backend/frontend, microservices, caching, queues, deployment, SaaS, integrations, workflows",
}

TECH_EDUCATION_DIRECTION = """
AI & TECHNOLOGY EDUCATION:
Teach practical knowledge to students, interns, developers, software engineers and working professionals.
Use any explicit audience and experience level in the brief; otherwise explain for an early-career developer,
with a useful engineering takeaway for experienced viewers. Do not mix every audience level into one lesson.
Keep the selected topic primary. Choose one clear learning objective and teach it within the requested format.
For a multi-scene lesson: introduce a real problem, define the concept in plain language, walk through a small
concrete example, explain the result, then finish with a practical takeaway or exercise. For a single post,
teach one self-contained concept and example. For a quote, use an original, useful engineering insight.
Define unfamiliar acronyms on first use. Explain why and when a technique helps, its limitations and relevant
tradeoffs. Use accurate terminology and distinguish AI models, agents, automation and ordinary software.
Adapt examples to the topic: code behavior, debugging, API request/response flow, data handling, model
evaluation or deployment decisions. Do not turn every lesson into a tool list, product promotion or career advice.
Prioritize technical accuracy and learning over cinematic drama, emotional hooks and engagement goals.
Avoid job-replacement fear, miracle productivity claims and unsupported benchmark or salary figures.
Do not invent API methods, executable code output, sources, release details or claims of being current.
Label conceptual pseudocode as pseudocode; mention relevant version assumptions for version-dependent examples.
Keep code short and explain its behavior in narration. Preserve code identifiers while using the requested
language for explanations. Never claim an example was tested when no execution evidence is supplied.
Plan visuals that explain the concept: a readable code walkthrough, diagram, request flow, debugger or
comparison. Do not imply generic typing footage proves code behavior. Avoid unrelated robots, neon brains
and futuristic imagery. Stock footage is context only; if the exact technical visual needs a custom diagram
or screen recording, describe it in visual_plan and leave unsuitable stock search fields empty.
""".strip()


def tech_education_direction(*identities):
    """Recognize existing tech brands and niche names without matching topic text."""
    aliases = {"ystech", "ystechcode", "aitechnology", "aiandtechnology", "aitech", "technology",
               "artificialintelligence", "ai", "softwareengineering", "softwaredevelopment",
               "programming", "coding"}
    for identity in identities:
        key = "".join(char for char in str(identity or "").casefold() if char.isalnum())
        if key in aliases:
            return TECH_EDUCATION_DIRECTION
    return ""


BRAND_CONTENT_PROFILES = {
    "finlogic": ("Money mistakes, saving, investing basics, financial psychology, budgeting, debt and practical financial decisions.",
                 "Turn a concrete money decision into a usable calculation, comparison or checklist; explain assumptions and risk without promising returns.",
                 "Simple money lessons people can actually use."),
    "zenhack": ("Mindset, habits, clarity, discipline, stress, self-growth and practical life lessons.",
                "Start from a recognizable moment of friction and offer a small action or experiment; show what changes rather than offering empty motivation.",
                "Practical mindset and self-growth lessons."),
    "psychopathcc": ("Psychology, human behavior, emotions, cognitive biases and relationships between thoughts and actions.",
                    "Connect a familiar behavior to a carefully explained mechanism and a useful reflection; distinguish evidence from interpretation and avoid diagnosing viewers.",
                    "Understand everyday behavior and the link between thoughts, feelings and actions."),
    "intimacyindex": ("Realistic relationship situations, communication, attraction, emotional connection, boundaries and misunderstandings.",
                      "Use a believable interaction, explain both perspectives and offer concrete words or a boundary to try; avoid manipulation and universal claims about partners.",
                      "Practical ways to communicate, build mutual connection and maintain healthy boundaries."),
    "cosmicnight": ("Space phenomena, astronomy facts, cosmic scale, mysteries, planets, stars and black holes.",
                    "Use cinematic science storytelling with a precise scale comparison or explained phenomenon; distinguish established science from open questions and never invent surprising facts.",
                    "Understand the universe through memorable, accurate space stories."),
    "ystechcode": ("AI, software engineering, APIs, coding, debugging, automation, backend development, developer mistakes and practical workflows.",
                   "Teach a specific engineering problem through a small example, failure mode, fix and tradeoff appropriate to the viewer's experience.",
                   "Practical AI, coding, API and automation knowledge for students, interns, developers and professionals."),
}


def brand_content_direction(niche, brand=None):
    normalize = lambda value: "".join(c for c in str(value or "").casefold() if c.isalnum())
    aliases = {"finlogicmoney": "finlogic", "ystech": "ystechcode"}
    name = getattr(brand, "name", None) or niche
    profile = None
    for identity in (getattr(brand, "name", None), niche, getattr(brand, "niche", None)):
        key = normalize(identity)
        profile = BRAND_CONTENT_PROFILES.get(aliases.get(key, key))
        if profile:
            break
    context = f"Selected brand: {name}. Brand context: {getattr(brand, 'description', None) or 'Use the selected niche and audience; do not invent brand credentials.'}"
    if profile:
        scope, treatment, promise = profile
        return f"{context}\nEditorial scope: {scope}\nBrand treatment: {treatment}\nRecurring audience benefit: {promise}"
    return context + f"\nDevelop a specific editorial approach and recurring audience benefit for {niche}. Keep the selected brand name; do not imitate another brand's voice or promise."


ENGAGEMENT_QUALITY_RULES = """
CONTENT VALUE CONTRACT — applies to every brand, format and content goal, including when no goal is selected:
1. STRONG HOOK: Put a specific scroll-stopping opening in hook and in the first scene's visible copy;
for video, open the narration with the same promise. The caption opening must also earn attention.
Use an honest curiosity gap, common mistake, relatable situation, concrete problem, supported surprise or
clear benefit. Skip greetings and generic introductions. Deliver the promised answer in this piece.
2. CLEAR USER BENEFIT: Internally answer 'Why should this viewer care?' Give an actionable step, useful
knowledge, emotional recognition, entertainment or a solution, demonstrated through a concrete example.
3. SPECIFIC ANGLE: Narrow the selected topic to one audience situation, decision, mechanism or mistake.
Reject standalone filler such as 'Save money every month', 'Stay positive' or 'AI is changing the world'.
Teach the particular action, reason or consequence. Never invent facts, statistics or urgency to make a hook.
4. NATURAL SHARE/SAVE VALUE: Every piece needs at least one inherent trigger: a relatable situation,
useful checklist, supported surprising insight, myth versus fact, common mistake, meaningful before/after,
identity recognition or a reference worth keeping. Choose internally; do not return a trigger label.
Do not force 'share this' into every caption. A CTA cannot substitute for substance.
5. FOLLOW REASON: Make the selected brand's recurring benefit clear in the caption, description or cta,
using its actual name when available. Explain what viewers will keep getting, not just 'follow for more'.
Vary the wording and placement; a clear brand promise can be implicit without an explicit follow request.
Give a natural reason to Like (recognition), Follow (recurring value), Save (reuse), Share (help someone)
or Comment (a meaningful experience/question). Do not demand all five actions or use engagement bait.
Honor the selected goal as the primary invitation while preserving the benefit and brand promise.
6. FORMAT AND BRAND FIT: Use the selected brand treatment, not one universal story formula. Keep the
requested language and format. For quotes and single images, keep visible copy concise and self-contained;
put supporting benefit and brand promise in the caption. On YouTube keep caption as the short video title;
put the follow reason and optional invitation in description or cta. Never replace the final payoff with a CTA.
7. INTERNAL QUALITY GATE: Before returning, check: strong hook? specific topic? clear benefit? useful,
emotional, entertaining or surprising substance? a save/share reason? clear recurring brand benefit?
distinct from generic AI filler? Does the body deliver the hook's promise? If any answer is No, rewrite
the content internally and recheck before returning. Return only the existing JSON fields, no scores,
checklists, analysis or additional keys. Self-review is not permission to fabricate a stronger claim.
Avoid repetitive openings, empty inspiration, unnecessary jargon, unsupported clickbait, reused visual
concepts and identical CTAs. Compare with supplied recent outputs; change the angle, not only punctuation.
""".strip()


SYSTEM_PROMPT = """
You are ViralForge AI.
Create specific, accurate, useful content for the selected brand and audience.
Earn attention with an honest hook and deliver its payoff in the same piece.
Choose the storytelling approach for the brand: technical clarity, practical decisions,
emotional recognition or cinematic science as appropriate to the brief.
Give each selected platform and format its own angle, caption and visual treatment.
Engagement must come from delivered value, not generic hype or unsupported claims.
Generate only the requested content and always return the existing valid JSON shape.
"""
