export default function ScriptStep({ content, onChange, busy }) {
    const youtube = content.platform?.toLowerCase() === "youtube";
    const field = "mt-2 block w-full rounded-xl border border-slate-300 bg-white p-3 text-sm";
    const changeScene = (id, key, value) => onChange({ ...content, scenes: content.scenes.map((scene) => scene.id === id ? { ...scene, [key]: value } : scene) });
    return <fieldset disabled={busy} className="space-y-5">
        <div><h2 className="text-xl font-bold">Review your script</h2><p className="mt-1 text-sm text-slate-500">Edit the copy and individual scenes. Continue saves these changes as a draft.</p></div>
        <div className="grid gap-4 sm:grid-cols-2">{[["title", "Title", 1], ["hook", "Opening hook", 2], ["script", "Full script", 4], ["caption", youtube ? "YouTube title (from caption, max 100 characters)" : "Post caption", youtube ? 2 : 4], ...(youtube ? [["description", "YouTube description", 5]] : []), ["hashtags", "Hashtags", 2], ["keywords", "Search keywords / tags", 2], ["cta", "Call to action", 2]].map(([name, label, rows]) => <label key={name} className="text-sm font-medium">{label}<textarea className={field} rows={rows} value={Array.isArray(content[name]) ? content[name].join(", ") : content[name] || ""} onChange={(e) => onChange({ ...content, [name]: e.target.value })} /></label>)}</div>
        <h3 className="font-semibold">Scene copy and narration</h3>
        {content.scenes.map((scene, index) => <article key={scene.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="mb-3 text-sm font-semibold">Scene {index + 1}</p>
            <div className="grid gap-4 sm:grid-cols-2">
                <label className="text-sm">Visible overlay text<textarea className={field} rows={3} value={scene.text || ""} onChange={(e) => changeScene(scene.id, "text", e.target.value)} /></label>
                <label className="text-sm">Spoken narration<textarea className={field} rows={3} value={scene.voice_text ?? scene.text ?? ""} onChange={(e) => changeScene(scene.id, "voice_text", e.target.value)} /></label>
                <label className="text-sm">Duration in seconds<input type="number" min="1" max="180" className={field} value={scene.duration ?? 5} onChange={(e) => changeScene(scene.id, "duration", e.target.value)} /></label>
                <label className="text-sm">Transition<select className={field} value={scene.transition || "fade"} onChange={(e) => changeScene(scene.id, "transition", e.target.value)}><option value="fade">Fade</option><option value="none">Cut</option></select></label>
            </div>
        </article>)}
    </fieldset>;
}
