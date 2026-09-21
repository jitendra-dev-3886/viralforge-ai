// Editorial suggestions, not live popularity rankings.
const MUSIC_KEYWORDS = [
    [/meditat|yoga|sleep|relax|breath|ध्यान|योग|नींद/i, ["calm ambient", "meditation flute", "soft piano"]],
    [/fitness|workout|sport|gym|exercise|फिटनेस|व्यायाम/i, ["energetic workout", "sport electronic", "motivational beat"]],
    [/travel|nature|adventure|mountain|यात्रा|प्रकृति/i, ["cinematic travel", "acoustic adventure", "ambient nature"]],
    [/educat|learn|tutorial|study|explain|शिक्षा|पढ़ाई/i, ["lofi study", "minimal background", "soft instrumental"]],
    [/business|finance|invest|market|productivity|व्यापार|निवेश/i, ["corporate inspiring", "minimal technology", "uplifting instrumental"]],
    [/tech|coding|software|science|\bai\b/i, ["ambient technology", "digital electronic", "minimal synth"]],
    [/food|cook|recipe|baking|खाना|रेसिपी/i, ["happy cooking", "acoustic jazz", "upbeat kitchen"]],
    [/fashion|beauty|makeup|luxury/i, ["fashion lounge", "chill house", "elegant ambient"]],
    [/motivat|success|inspir|प्रेरणा/i, ["inspiring piano", "motivational cinematic", "uplifting epic"]],
    [/comedy|funny|humor|मजेदार/i, ["playful quirky", "funny pizzicato", "happy ukulele"]],
    [/devotion|spiritual|prayer|भक्ति|पूजा/i, ["spiritual flute", "peaceful meditation", "indian instrumental"]],
];

export function musicSearchSuggestions(content) {
    const config = content.generation_config || {};
    // The specific topic takes precedence over a broad niche (e.g. yoga in fitness).
    const sources = [config.topic, content.title, config.niche, content.script];
    const matches = sources.flatMap((text) => MUSIC_KEYWORDS.filter(([pattern]) => pattern.test(String(text || ""))).flatMap(([, terms]) => terms));
    const keywords = [...new Set(matches.length ? matches : ["soft lofi", "ambient background", "gentle acoustic"])].slice(0, 6);
    return keywords;
}

export function audioSuggestion(content) {
    const config = content.generation_config || {};
    const text = `${config.niche || ""} ${config.topic || ""} ${content.title || ""} ${content.script || ""}`.toLowerCase();
    if (/fitness|workout|sport|gym|energy/.test(text)) return { mood: "Energetic electronic", query: "energetic sport instrumental", speed: "+10%", reason: "A steady beat supports fast movement; a brisk voice suits short action cues." };
    if (/meditat|yoga|sleep|wellness|calm/.test(text)) return { mood: "Calm ambient", query: "calm ambient meditation", speed: "-10%", reason: "Gentle instrumental textures and slower narration leave room for pauses." };
    if (/travel|nature|adventure|story/.test(text)) return { mood: "Cinematic acoustic", query: "cinematic acoustic travel", speed: "-5%", reason: "An atmospheric instrumental bed supports scenic footage and storytelling." };
    if (/fashion|food|lifestyle|beauty/.test(text)) return { mood: "Warm upbeat groove", query: "upbeat chill instrumental", speed: "+5%", reason: "A light groove supports lively demonstrations without competing with speech." };
    return { mood: "Soft lo-fi / minimal", query: "soft lofi instrumental background", speed: "+0%", reason: "Low-key instrumental music leaves space for clear explanations and narration." };
}
