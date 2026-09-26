import { apiErrorMessage } from "../../api/errors.js";
import { CONTENT_GOALS } from "../ai/contentGoals.js";

export const STEPS = ["Brief", "Script", "Media", "Voice", "Design & export", "Schedule"];
export const FORMATS = {
    Instagram: ["Reel", "Carousel", "Story", "Post", "Quote"],
    Facebook: ["Reel", "Carousel", "Story", "Post", "Quote"],
    YouTube: ["Shorts", "Long Video", "Community Post"],
};
export const INITIAL_BRIEF = { projectId: "", platform: "Instagram", format: "Reel", topic: "", niche: "", language: "English", tone: "Educational", scenes: 5, duration: 30, provider: "auto", visualStyle: "minimal", contentGoal: "" };
export const isVideoFormat = (format) => /reel|short|story|video/i.test(format);
export function publishingAssets(content, media) {
    const video = isVideoFormat(content.content_type || "");
    const pattern = new RegExp(video ? `^content_${Number(content.id)}_final\\.mp4$` : `^content_${Number(content.id)}_scene_(\\d+)_final\\.(?:png|jpe?g|webp)$`, "i");
    const latest = new Map();
    for (const item of media) {
        const match = pattern.exec(item.file_name || "");
        if (!match || item.status !== "ready" || (video ? item.media_type !== "final" : item.media_type !== "image")) continue;
        const order = video ? 0 : Number(match[1]);
        if (!latest.has(order) || Number(item.id) > Number(latest.get(order).id)) latest.set(order, item);
    }
    return [...latest.entries()].sort(([a], [b]) => a - b).map(([, item]) => item);
}
export function publishingSelectionError(content, selected, scenes = content.scenes || []) {
    const format = (content.content_type || "").toLowerCase();
    const platform = (content.platform || "").toLowerCase();
    if (platform === "youtube" && !/short|video/.test(format)) return "This format needs manual publishing on YouTube. Save a manual reminder instead.";
    if (format === "story") return "Automatic Story publishing is not supported here. Save a manual reminder.";
    if (format.includes("carousel")) {
        const expected = scenes.map(scene => Number(scene.scene_number || scene.scene)).sort((a, b) => a - b);
        const actual = selected.map(item => Number(item.file_name.match(/_scene_(\d+)_final/i)?.[1]));
        if (expected.length < 2 || expected.length > 10) return "Automatic carousels need 2–10 slides.";
        if (actual.length !== expected.length || actual.some((number, i) => number !== expected[i])) return "Export and select every carousel slide in scene order.";
    } else if (selected.length !== 1) return isVideoFormat(format) ? "Export and select one complete final video." : "Export and select one finished image.";
    return "";
}
export function generationPayload(brief) {
    if (!Number(brief.projectId) || !brief.topic.trim() || !brief.niche.trim()) throw new Error("Choose a project, niche and topic first.");
    if (!FORMATS[brief.platform]?.includes(brief.format)) throw new Error("Choose a format supported by the platform.");
    if (brief.contentGoal && !CONTENT_GOALS.includes(brief.contentGoal)) throw new Error("Choose a supported content goal.");
    const packageType = brief.format === "Quote" ? "quote" : brief.format === "Carousel" ? "carousel" : brief.format === "Story" ? "story" : isVideoFormat(brief.format) ? "reel" : "complete";
    return {
        project_id: Number(brief.projectId), platforms: [brief.platform], content_types: [brief.format],
        outputs: [`${brief.platform}: ${brief.format}`], topic: brief.topic.trim(), niche: brief.niche.trim(),
        package: packageType, language: brief.language, style: brief.tone, provider: brief.provider,
        visual_style: brief.visualStyle,
        ...(brief.contentGoal ? { content_goal: brief.contentGoal } : {}),
        scene_count: ["Quote", "Post", "Community Post"].includes(brief.format) ? 1 : Number(brief.scenes),
        ...(isVideoFormat(brief.format) ? { total_duration: Number(brief.duration) } : {}),
    };
}
export function assertSuccess(result) {
    if (result?.success === false) throw new Error(result.message || "The operation could not be completed.");
    return result;
}
export function errorMessage(error) {
    return apiErrorMessage(error, "Something went wrong. Please retry.");
}
export function contentPatch(content) {
    return Object.fromEntries(["title", "hook", "script", "caption", "hashtags", "keywords", "cta", ...(Object.hasOwn(content, "description") ? ["description"] : [])].map((name) => [name, Array.isArray(content[name]) ? content[name].join(",") : content[name] || ""]));
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
