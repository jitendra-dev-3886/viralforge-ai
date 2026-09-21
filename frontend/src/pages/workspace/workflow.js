export const STEPS = ["Brief", "Script", "Media", "Voice", "Design & export", "Schedule"];
export const FORMATS = {
    Instagram: ["Reel", "Carousel", "Story", "Post", "Quote"],
    Facebook: ["Reel", "Carousel", "Story", "Post", "Quote"],
    YouTube: ["Shorts", "Long Video", "Community Post"],
};
export const INITIAL_BRIEF = { projectId: "", platform: "Instagram", format: "Reel", topic: "", niche: "", language: "English", tone: "Educational", scenes: 5, duration: 30, provider: "auto", visualStyle: "minimal" };
export const isVideoFormat = (format) => /reel|short|story|video/i.test(format);
export function generationPayload(brief) {
    if (!Number(brief.projectId) || !brief.topic.trim() || !brief.niche.trim()) throw new Error("Choose a project, niche and topic first.");
    if (!FORMATS[brief.platform]?.includes(brief.format)) throw new Error("Choose a format supported by the platform.");
    const packageType = brief.format === "Quote" ? "quote" : brief.format === "Carousel" ? "carousel" : brief.format === "Story" ? "story" : isVideoFormat(brief.format) ? "reel" : "complete";
    return {
        project_id: Number(brief.projectId), platforms: [brief.platform], content_types: [brief.format],
        outputs: [`${brief.platform}: ${brief.format}`], topic: brief.topic.trim(), niche: brief.niche.trim(),
        package: packageType, language: brief.language, style: brief.tone, provider: brief.provider,
        visual_style: brief.visualStyle,
        scene_count: ["Quote", "Post", "Community Post"].includes(brief.format) ? 1 : Number(brief.scenes),
        ...(isVideoFormat(brief.format) ? { total_duration: Number(brief.duration) } : {}),
    };
}
export function assertSuccess(result) {
    if (result?.success === false) throw new Error(result.message || "The operation could not be completed.");
    return result;
}
export function errorMessage(error) {
    const detail = error.response?.data?.detail;
    return typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((item) => item.msg).join(". ") : detail?.message || error.message || "Something went wrong. Please retry.";
}
export function contentPatch(content) {
    return Object.fromEntries(["title", "hook", "script", "caption", "hashtags", "keywords", "cta"].map((name) => [name, Array.isArray(content[name]) ? content[name].join(",") : content[name] || ""]));
}
export function scenePatch(scene) {
    const duration = Number(scene.duration);
    if (!scene.text?.trim()) throw new Error("Every scene needs overlay text.");
    if (!Number.isFinite(duration) || duration < 1 || duration > 180) throw new Error("Scene duration must be between 1 and 180 seconds.");
    return { text: scene.text, voice_text: scene.voice_text ?? scene.text, duration, transition: scene.transition || "fade" };
}
export function latestVoices(voices, contentId) {
    const result = {};
    [...voices].filter((voice) => Number(voice.content_id) === Number(contentId) && voice.status === "generated")
        .sort((a, b) => String(b.updated_at || b.created_at || "").localeCompare(String(a.updated_at || a.created_at || "")) || b.id - a.id)
        .forEach((voice) => { result[voice.scene_id] ??= voice; });
    return result;
}
export function staleVoiceScenes(content, voices) {
    const latest = latestVoices(voices, content?.id);
    return (content?.scenes || []).filter((scene) => latest[scene.id] && latest[scene.id].text?.trim() !== (scene.voice_text ?? scene.text ?? "").trim());
}
export function restoreDraft(server, draft) {
    if (!draft || Number(draft.id) !== Number(server.id)) return server;
    return { ...server, ...contentPatch(draft), scenes: server.scenes.map((scene) => {
        const local = draft.scenes?.find((item) => item.id === scene.id);
        return local ? { ...scene, text: local.text, voice_text: local.voice_text, duration: local.duration, transition: local.transition } : scene;
    }) };
}
