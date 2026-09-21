import test from "node:test";
import assert from "node:assert/strict";
import { INITIAL_BRIEF, generationPayload, contentPatch, scenePatch, latestVoices, staleVoiceScenes, restoreDraft, assertSuccess } from "./workflow.js";

const brief = { ...INITIAL_BRIEF, projectId: "7", topic: " Daily habits ", niche: "Education" };

test("generation targets exactly the selected platform and format", () => {
    const payload = generationPayload({ ...brief, platform: "YouTube", format: "Shorts", language: "Hindi", visualStyle: "cinematic" });
    assert.deepEqual(payload.outputs, ["YouTube: Shorts"]);
    assert.deepEqual(payload.content_types, ["Shorts"]);
    assert.equal(payload.project_id, 7);
    assert.equal(payload.language, "Hindi");
    assert.equal(payload.visual_style, "cinematic");
    assert.equal(payload.topic, "Daily habits");
    assert.throws(() => generationPayload({ ...brief, platform: "YouTube", format: "Carousel" }), /supported/);
});

test("single posts use one scene and no video duration", () => {
    for (const format of ["Post", "Quote"]) {
        const payload = generationPayload({ ...brief, format });
        assert.equal(payload.scene_count, 1);
        assert.equal("total_duration" in payload, false);
    }
    assert.throws(() => generationPayload({ ...brief, topic: " " }), /topic/);
});

test("copy edits do not overwrite media, branding, or approval status", () => {
    const patch = contentPatch({ title: "Edited", hashtags: ["#one", "#two"], status: "approved", generation_config: { visual_style: "bold" }, project_id: 99 });
    assert.equal(patch.hashtags, "#one,#two");
    assert.equal(patch.title, "Edited");
    assert.equal("generation_config" in patch, false);
    assert.equal("status" in patch, false);
    assert.equal("project_id" in patch, false);
});

test("scene validation happens before saving and preserves separate narration", () => {
    assert.deepEqual(scenePatch({ text: "Short overlay", voice_text: "A longer explanation", duration: "8", media_id: 15 }), { text: "Short overlay", voice_text: "A longer explanation", duration: 8, transition: "fade" });
    assert.throws(() => scenePatch({ text: "", duration: 5 }), /overlay text/);
    assert.throws(() => scenePatch({ text: "Hello", duration: "invalid" }), /duration/);
});

test("only the newest successful narration for this content affects readiness", () => {
    const content = { id: 3, scenes: [{ id: 8, text: "Overlay", voice_text: "New narration" }] };
    const voices = [
        { id: 1, content_id: 3, scene_id: 8, status: "generated", text: "Old narration" },
        { id: 2, content_id: 3, scene_id: 8, status: "generated", text: "New narration" },
        { id: 3, content_id: 3, scene_id: 8, status: "failed", text: "Wrong" },
        { id: 4, content_id: 7, scene_id: 8, status: "generated", text: "Other content" },
    ];
    assert.equal(latestVoices(voices, 3)[8].id, 2);
    assert.equal(staleVoiceScenes(content, voices).length, 0);
    content.scenes[0].voice_text = "Edited again";
    assert.equal(staleVoiceScenes(content, voices).length, 1);
    assert.equal(staleVoiceScenes(content, []).length, 0);
});

test("restoring a draft keeps fresh media and does not resurrect deleted scenes", () => {
    const server = { id: 3, title: "Saved", generation_config: { visual_style: "bold" }, scenes: [{ id: 8, text: "Saved", media_url: "/new.png", media_id: 42 }] };
    const draft = { id: 3, title: "Local edit", scenes: [{ id: 8, text: "Local scene", duration: 6, media_url: "/old.png" }, { id: 9, text: "Deleted" }] };
    const restored = restoreDraft(server, draft);
    assert.equal(restored.title, "Local edit");
    assert.equal(restored.scenes.length, 1);
    assert.equal(restored.scenes[0].text, "Local scene");
    assert.equal(restored.scenes[0].media_id, 42);
    assert.deepEqual(restored.generation_config, server.generation_config);
    assert.equal(restoreDraft(server, { ...draft, id: 4 }), server);
});

test("an HTTP 200 with success false is still treated as a failed save", () => {
    assert.throws(() => assertSuccess({ success: false, message: "Scene unavailable" }), /Scene unavailable/);
});
