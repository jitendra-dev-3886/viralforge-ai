import { getContent, updateContent } from "../../api/content";
import { getContentScenes, updateScene, downloadSceneMedia } from "../../api/scene";
import { assertSuccess, contentPatch, scenePatch } from "./workflow";

export async function loadWorkspaceContent(id) {
    const [result, sceneResult] = await Promise.all([getContent(id), getContentScenes(id)]);
    assertSuccess(result); assertSuccess(sceneResult);
    const content = result.content || result.data || result;
    if (!content.id) throw new Error("This content is unavailable. Choose another saved item.");
    return { ...content, scenes: (content.scenes || []).map((scene) => {
        const details = (sceneResult.scenes || []).find((item) => item.id === scene.id);
        return { ...scene, voice_text: details?.voice_text ?? scene.text, transition: details?.transition || "fade" };
    }) };
}

export async function saveWorkspaceContent(content) {
    // Validate everything before any request. Save only editable copy, not branding or media.
    const scenes = content.scenes.map((scene) => ({ id: scene.id, patch: scenePatch(scene) }));
    assertSuccess(await updateContent(content.id, { ...contentPatch(content), status: "draft" }));
    for (const scene of scenes) assertSuccess(await updateScene(scene.id, scene.patch));
    return loadWorkspaceContent(content.id);
}

export async function findSceneMedia(scene, keyword) {
    if (!keyword.trim()) throw new Error("Enter a stock-media search phrase.");
    assertSuccess(await updateScene(scene.id, { keyword: keyword.trim(), image_prompt: keyword.trim(), video_prompt: keyword.trim(), media_id: null }));
    try {
        return assertSuccess(await downloadSceneMedia(scene.id));
    } catch (error) {
        // A failed lookup should not discard the previously selected asset.
        assertSuccess(await updateScene(scene.id, { media_id: scene.media_id ?? null }));
        throw error;
    }
}
