import test from "node:test";
import assert from "node:assert/strict";
import { studioGenerationPayload } from "./studioGeneration.js";

const settings = {
    selectedProjectId: 7, selectedPlatforms: ["instagram", "youtube"],
    selectedContent: ["instagram:post", "youtube:shorts"], selectedNiche: "Education",
    selectedTopic: "Daily habits", selectedPackage: "complete", selectedProvider: "auto",
    visualStyle: "minimal", contentGoal: "Shares",
};

test("the selected language is sent for every package and every output", () => {
    for (const language of ["Hindi", "English", "Hinglish"]) {
        for (const selectedPackage of ["complete", "quote", "reel", "carousel", "story"]) {
            const payload = studioGenerationPayload({ ...settings, selectedPackage,
                generationOptions: { language, scene_count: 7, total_duration: 30, style: "Educational" } });
            assert.equal(payload.language, language);
            assert.deepEqual(payload.outputs, ["Instagram: Post", "YouTube: Shorts"]);
            assert.equal(payload.content_goal, "Shares");
            assert.equal(payload.project_id, 7);
        }
    }
});

test("package-specific scene and duration settings remain intact", () => {
    const generationOptions = { language: "Hindi", scene_count: 7, total_duration: 30, style: "Educational" };
    const complete = studioGenerationPayload({ ...settings, generationOptions });
    assert.equal(complete.scene_count, undefined);
    assert.equal(complete.total_duration, undefined);
    const reel = studioGenerationPayload({ ...settings, selectedPackage: "reel", generationOptions });
    assert.equal(reel.scene_count, 7);
    assert.equal(reel.total_duration, 30);
    assert.equal(reel.style, "Educational");
});
