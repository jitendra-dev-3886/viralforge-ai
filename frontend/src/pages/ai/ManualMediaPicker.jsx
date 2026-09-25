import { useState } from "react";
import { mediaFileError } from "./manualMedia";

export default function ManualMediaPicker({ outputs, files, onChange, disabled }) {
    const [error, setError] = useState("");
    return <fieldset disabled={disabled} className="mt-6 space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div><h2 className="text-lg font-semibold">Upload image or video (optional)</h2>
            <p className="mt-1 text-sm text-slate-500">Choose files for specific scenes before generating. Empty slots use the normal generated media. Files are applied once your scenes are created.</p>
            <p className="mt-1 text-xs text-slate-500">Images: JPG, PNG, WebP up to 20 MB. Videos: MP4, MOV, WebM up to 100 MB. Keep this page open until generation and uploads finish.</p></div>
        {!outputs.length && <p className="text-sm text-slate-500">Select a platform and content format above to choose scene uploads.</p>}
        {outputs.map(output => <div key={output.key} className="space-y-3">
            <h3 className="font-semibold">{output.label}</h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: output.count }, (_, index) => {
                const key = `${output.key}:${index}`;
                const file = files[key];
                return <div key={key} className="min-w-0 rounded-xl border border-slate-200 p-3">
                    <label className="block text-sm font-medium">{output.type === "carousel" ? "Slide" : "Scene"} {index + 1}
                        <input type="file" accept=".jpg,.jpeg,.png,.webp,.mp4,.mov,.webm" className="mt-2 block w-full text-xs file:mr-2 file:rounded-lg file:border-0 file:bg-indigo-50 file:p-2 file:text-indigo-700" onChange={event => {
                            const next = event.target.files?.[0]; event.target.value = "";
                            if (!next) return;
                            const message = mediaFileError(next); setError(message);
                            if (!message) onChange({ ...files, [key]: next });
                        }} />
                    </label>
                    {file ? <div className="mt-2 text-xs"><p className="break-all">{file.name}</p><button type="button" className="mt-1 text-red-600 underline" onClick={() => { const next = { ...files }; delete next[key]; onChange(next); }}>Remove file</button></div> : <p className="mt-2 text-xs text-slate-500">Use generated media</p>}
                </div>;
            })}</div>
        </div>)}
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
    </fieldset>;
}
