export function uploadSlotCount(type, packageType, selectedCount) {
    if (type === "quote" || (packageType === "quote" && type !== "carousel")) return 1;
    const count = ["reel", "carousel", "story"].includes(packageType) ? selectedCount : null;
    if (count) return type === "carousel" ? Math.max(3, count) : count;
    if (type === "carousel") return 6;
    if (["reel", "shorts", "story"].includes(type)) return 7;
    return type === "video" ? 10 : 5;
}

export function mediaFileError(file) {
    const extension = file.name.split(".").pop().toLowerCase();
    const image = ["jpg", "jpeg", "png", "webp"].includes(extension);
    if (!image && !["mp4", "mov", "webm"].includes(extension)) return "Choose a JPG, PNG, WebP, MP4, MOV, or WebM file.";
    if (!file.size) return "Choose a file that is not empty.";
    if (file.size > (image ? 20 : 100) * 1024 * 1024) return `File must be ${image ? 20 : 100} MB or smaller.`;
    return "";
}

// Match each file to its selected output and scene, including multi-platform packages.
export async function applyManualMedia(response, assignments, upload, loadContent) {
    const result = structuredClone(response);
    const failures = [];
    for (const assignment of assignments) {
        const { platform, format, index, file } = assignment;
        const normalize = value => value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
        const content = result.data?.title !== undefined ? result.data : result.data?.[normalize(platform)]?.[normalize(format)];
        try {
            if (!content) throw new Error("Generated output is unavailable.");
            if (!content.scenes?.[index]?.id) {
                const id = content.content_id || content.id || (result.data?.title !== undefined ? result.content_id : null);
                if (!id) throw new Error("Saved content is unavailable.");
                const saved = await loadContent(id);
                content.scenes = (saved.content || saved.data || saved).scenes;
            }
            const scene = content.scenes?.[index];
            if (!scene?.id) throw new Error("Saved scene is unavailable.");
            const media = await upload(scene.id, file);
            if (media.success === false) throw new Error("Upload failed.");
            Object.assign(scene, media);
        } catch {
            failures.push(`${platform} ${format}, scene ${index + 1}`);
        }
    }
    return { result, failures };
}
