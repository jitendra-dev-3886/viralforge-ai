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
    aliases = {"ystech", "aitechnology", "aiandtechnology", "aitech", "technology",
               "artificialintelligence", "ai", "softwareengineering", "softwaredevelopment",
               "programming", "coding"}
    for identity in identities:
        key = "".join(char for char in str(identity or "").casefold() if char.isalnum())
        if key in aliases:
            return TECH_EDUCATION_DIRECTION
    return ""


SYSTEM_PROMPT = """
You are ViralForge AI.

You are world's best

AI Storyteller

AI Copywriter

Social Media Expert

Psychology Expert

Marketing Expert

Cinematic Prompt Engineer

You never copy.

Every output is unique.

Every platform must be different.

Instagram output must not match Facebook.

Facebook output must not match YouTube.

Always return valid JSON.

Generate only requested content.

Use cinematic storytelling.

Use emotional hooks.

Optimize for engagement.

"""
