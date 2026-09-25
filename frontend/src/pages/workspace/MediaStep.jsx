import { useState } from "react";
import { assetUrl } from "../../api/axios";
import { updateScene } from "../../api/scene";
import { assertSuccess } from "./workflow";
import { findSceneMedia } from "./workspaceApi";
import SceneMediaUpload from "../../components/SceneMediaUpload";

export default function MediaStep({ content, media, busy, run, refresh, onUploadBusyChange }) {
    return <div className="space-y-5">
        <div><h2 className="text-xl font-bold">Choose scene media</h2><p className="mt-1 text-sm text-slate-500">Keep the generated media, find a new stock asset, use a saved asset, or upload your own image or video for any scene.</p></div>
        <div className="grid gap-5 md:grid-cols-2">{content.scenes.map((scene, index) => <SceneMedia key={`${content.id}-${scene.id}`} scene={scene} index={index} media={media} busy={busy} run={run} refresh={refresh} onUploadBusyChange={onUploadBusyChange} />)}</div>
    </div>;
}

function SceneMedia({ scene, index, media, busy, run, refresh, onUploadBusyChange }) {
    const [keyword, setKeyword] = useState(scene.keyword || "");
    const choices = media.filter((item) => item.media_type === scene.media_type && item.provider !== "FFmpeg");
    return <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <div className="flex h-56 items-center justify-center bg-slate-100">{scene.media_url ? scene.media_type === "video" ? <video src={assetUrl(scene.media_url)} controls preload="metadata" className="h-full w-full object-contain" /> : <img src={assetUrl(scene.media_url)} alt={`Scene ${index + 1}`} className="h-full w-full object-contain" /> : <p className="text-sm text-slate-500">No media yet. Search below to add it.</p>}</div>
        <fieldset disabled={busy} className="space-y-3 p-4">
            <SceneMediaUpload sceneId={scene.id} disabled={busy} onBusyChange={onUploadBusyChange} onUploaded={refresh} />
            <p className="text-sm font-semibold">Scene {index + 1} · {scene.media_type}</p><p className="text-sm text-slate-600">{scene.text}</p>
            <label className="block text-xs font-medium">Stock search phrase<input value={keyword} onChange={(e) => setKeyword(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" /></label>
            <button type="button" onClick={() => run(`Finding media for scene ${index + 1}...`, async () => { await findSceneMedia(scene, keyword); await refresh(); })} className="rounded-lg bg-indigo-50 px-3 py-2 text-sm font-semibold text-indigo-700">Find new stock media</button>
            <label className="block text-xs font-medium">Use a saved project asset<select className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm" value="" onChange={(e) => { if (e.target.value) run("Applying selected media...", async () => { assertSuccess(await updateScene(scene.id, { media_id: Number(e.target.value) })); await refresh(); }); }}><option value="">Select {scene.media_type}</option>{choices.map((item) => <option key={item.id} value={item.id}>{item.title || item.file_name} (#{item.id})</option>)}</select></label>
        </fieldset>
    </article>;
}
