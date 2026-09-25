import test from "node:test";
import assert from "node:assert/strict";
import { applyManualMedia, mediaFileError, uploadSlotCount } from "./manualMedia.js";

test("upload slots match format and package scene counts", () => {
    assert.equal(uploadSlotCount("carousel", "carousel", 10), 10);
    assert.equal(uploadSlotCount("quote", "carousel", 10), 1);
    assert.equal(uploadSlotCount("carousel", "complete", 7), 6);
    assert.equal(uploadSlotCount("video", "complete", 7), 10);
    assert.equal(uploadSlotCount("reel", "reel", 3), 3);
});

test("only assigned scenes are replaced in the correct output", async () => {
    const response = { data: {
        instagram: { carousel: { title: "Slides", scenes: [{ id: 1, media_url: "auto1" }, { id: 2, media_url: "auto2" }] } },
        youtube: { long_video: { title: "Video", scenes: [{ id: 3, media_url: "auto3" }] } },
    } };
    const calls = [];
    const { result, failures } = await applyManualMedia(response, [
        { platform: "Instagram", format: "Carousel", index: 1, file: "image" },
        { platform: "YouTube", format: "Long Video", index: 0, file: "video" },
    ], async (id, file) => { calls.push([id, file]); return { media_url: file }; });
    assert.deepEqual(calls, [[2, "image"], [3, "video"]]);
    assert.equal(result.data.instagram.carousel.scenes[0].media_url, "auto1");
    assert.equal(result.data.instagram.carousel.scenes[1].media_url, "image");
    assert.equal(response.data.instagram.carousel.scenes[1].media_url, "auto2");
    assert.deepEqual(failures, []);
});

test("failed upload preserves generated media and later uploads continue", async () => {
    const response = { data: { title: "Test", scenes: [{ id: 1, media_url: "auto" }, { id: 2 }] } };
    const assignments = [0, 1].map(index => ({ platform: "Instagram", format: "Reel", index, file: "video" }));
    const { result, failures } = await applyManualMedia(response, assignments, async id => {
        if (id === 1) throw new Error("Upload failed");
        return { media_url: "uploaded" };
    });
    assert.equal(result.data.scenes[0].media_url, "auto");
    assert.equal(result.data.scenes[1].media_url, "uploaded");
    assert.deepEqual(failures, ["Instagram Reel, scene 1"]);
});

test("missing scene IDs are loaded from the saved content before uploading", async () => {
    const response = { content_id: 4, data: { title: "Test", scenes: [{ text: "Hello" }] } };
    const { result } = await applyManualMedia(response, [{ platform: "Instagram", format: "Post", index: 0, file: "image" }],
        async id => { assert.equal(id, 7); return { media_url: "uploaded" }; },
        async id => { assert.equal(id, 4); return { content: { scenes: [{ id: 7 }] } }; });
    assert.equal(result.data.scenes[0].media_url, "uploaded");
});

test("no selected files leaves generation untouched", async () => {
    const response = { data: { title: "Test", scenes: [{ id: 1 }] } };
    const { result } = await applyManualMedia(response, [], () => assert.fail("Unexpected upload"));
    assert.deepEqual(result, response);
});

test("file picker rejects unsupported, empty and oversized files", () => {
    assert.ok(mediaFileError({ name: "bad.svg", size: 5 }));
    assert.ok(mediaFileError({ name: "empty.png", size: 0 }));
    assert.ok(mediaFileError({ name: "large.jpg", size: 21 * 1024 * 1024 }));
    assert.equal(mediaFileError({ name: "clip.mp4", size: 50 * 1024 * 1024 }), "");
});
