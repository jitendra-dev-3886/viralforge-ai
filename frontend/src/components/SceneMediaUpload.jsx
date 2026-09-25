import { useRef, useState } from "react";
import { uploadSceneMedia } from "../api/scene";

export default function SceneMediaUpload({ sceneId, disabled, onUploaded, onBusyChange }) {
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState("");
    const lock = useRef(false);
    const upload = async (event) => {
        const file = event.target.files?.[0];
        event.target.value = "";
        if (!file || lock.current) return;
        const extension = file.name.split(".").pop().toLowerCase();
        const image = ["jpg", "jpeg", "png", "webp"].includes(extension);
        if (!image && !["mp4", "mov", "webm"].includes(extension)) { setMessage("Choose a JPG, PNG, WebP, MP4, MOV, or WebM file."); return; }
        if (file.size > (image ? 20 : 100) * 1024 * 1024) { setMessage(`File must be ${image ? 20 : 100} MB or smaller.`); return; }
        lock.current = true; setBusy(true); setMessage(""); onBusyChange?.(true);
        try {
            const result = await uploadSceneMedia(sceneId, file);
            await onUploaded(result);
            setMessage("Uploaded media saved for this scene.");
        } catch (error) { setMessage(error.response?.data?.detail || "Upload failed. Please try again."); }
        finally { lock.current = false; setBusy(false); onBusyChange?.(false); }
    };
    return <div className="mt-3 space-y-2">
        <label className="block text-xs font-semibold">Upload image or video (optional)
            <input type="file" accept=".jpg,.jpeg,.png,.webp,.mp4,.mov,.webm" disabled={disabled || busy || !sceneId} onChange={upload} className="mt-2 block w-full text-xs file:mr-2 file:rounded-lg file:border-0 file:bg-indigo-50 file:p-2 file:text-indigo-700 disabled:opacity-50" />
        </label>
        <p className="text-xs text-slate-500">Images up to 20 MB; video clips up to 100 MB. Skip to keep the current media.</p>
        {!sceneId && <p role="status" className="text-xs text-amber-700">Upload will be available when this scene's saved details are loaded.</p>}
        {(busy || message) && <p role="status" className="text-xs text-indigo-700">{busy ? "Uploading media..." : message}</p>}
    </div>;
}
