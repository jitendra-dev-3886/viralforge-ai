import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createSchedule, deleteSchedule, getSchedules, updateSchedule } from "../../api/schedule";
import { getAllContents, updateContent } from "../../api/content";
import { getPostingEvents } from "../../api/social";
import AutoPostForm from "./AutoPostForm";
import { apiErrorMessage } from "../../api/errors";

export default function Scheduler() {
    const [items, setItems] = useState([]);
    const [contents, setContents] = useState([]);
    const [contentId, setContentId] = useState("");
    const [when, setWhen] = useState("");
    const [mode, setMode] = useState("automatic");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [events, setEvents] = useState({});
    const load = useCallback(async () => {
        const [schedules, content] = await Promise.all([getSchedules(), getAllContents()]);
        setItems(schedules.schedules || []); setContents(content.contents || []);
    }, []);
    useEffect(() => {
        load().catch(err => setError(apiErrorMessage(err, "Unable to load scheduler.")));
        const timer = setInterval(() => getSchedules().then(result => setItems(result.schedules || [])).catch(() => {}), 15000);
        return () => clearInterval(timer);
    }, [load]);
    const action = async task => {
        setBusy(true); setError("");
        try { await task(); } catch (err) { setError(apiErrorMessage(err, "Unable to update schedule.")); }
        finally { setBusy(false); }
    };
    const selected = contents.find(item => item.id === Number(contentId));
    return <div className="space-y-6 p-1 sm:p-4 lg:p-8">
        <header className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="text-3xl font-bold">Scheduler</h1><p className="mt-2 text-slate-500">Schedule approved content and track every automatic post.</p></div><Link to="/settings#social-accounts" className="rounded-xl border bg-white px-4 py-3 text-sm text-indigo-600">Connect Instagram, Facebook or YouTube</Link></header>
        {error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
        <section className="space-y-4 rounded-2xl bg-white p-5 shadow-sm">
            <label className="block text-sm font-semibold">Content<select value={contentId} onChange={event => { setContentId(event.target.value); setNotice(""); }} className="mt-2 block w-full rounded-xl border p-3"><option value="">Select generated content</option>{contents.map(content => <option key={content.id} value={content.id}>{content.title} ? {content.platform} ({content.status})</option>)}</select></label>
            {!contents.length && <p className="text-sm text-slate-500">Generate content in AI Studio or Creation Workspace first.</p>}
            <label className="block text-sm font-semibold">Posting method<select value={mode} onChange={event => setMode(event.target.value)} className="mt-2 block w-full rounded-xl border p-3"><option value="automatic">Automatic ? publish to a connected account</option><option value="manual">Manual ? save a reminder only</option></select></label>
            {selected && selected.status !== "approved" && <div className="space-y-3 rounded-xl bg-amber-50 p-4">
                <p className="text-sm">Review this content before approving it for posting.</p>
                <p className="font-medium">{selected.title}</p>
                <p className="max-h-48 overflow-y-auto whitespace-pre-wrap text-sm">{selected.script}</p>
                <p className="whitespace-pre-wrap text-sm">{selected.caption}</p>
                <Link to={`/content/${selected.id}/edit`} className="mr-4 text-sm text-indigo-600 underline">Review scenes and edit</Link>
                <button type="button" disabled={busy} onClick={() => action(async () => {
                    const result = await updateContent(selected.id, { status: "approved" });
                    if (result.success === false) throw new Error(result.message || "Unable to approve content.");
                    await load();
                    setNotice("Content approved. Choose your media and posting time below.");
                })} className="rounded-xl bg-emerald-600 px-4 py-2 text-sm text-white disabled:opacity-40">Approve content</button>
            </div>}
            {selected && (mode === "automatic" ? <AutoPostForm key={selected.id} content={selected} disabled={busy} onScheduled={async () => { setNotice("Upload scheduled. Its visibility, status and posting record are shown below."); await load(); }} /> : <form onSubmit={event => { event.preventDefault(); action(async () => { await createSchedule({ project_id: selected.project_id, content_id: selected.id, platform: selected.platform, scheduled_at: new Date(when).toISOString(), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone }); setWhen(""); setNotice("Manual reminder saved. It will not publish automatically."); await load(); }); }} className="flex flex-wrap gap-3"><input aria-label="Manual reminder time" type="datetime-local" required value={when} onChange={event => setWhen(event.target.value)} className="rounded-xl border p-3" /><button disabled={busy || selected.status !== "approved"} className="rounded-xl bg-slate-900 px-4 py-3 text-sm text-white">Save manual reminder</button></form>)}
        </section>
        <h2 className="text-xl font-semibold">Posting records</h2>
        {!items.length && <p className="rounded-2xl border border-dashed p-8 text-center text-slate-500">No scheduled posts yet.</p>}
        <div className="space-y-3">{items.map(item => <article key={item.id} className="space-y-3 rounded-2xl bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3"><div><strong>{item.title || `Content #${item.content_id}`}</strong><p className="mt-1 text-sm capitalize text-slate-500">{item.platform} ? {item.account_name || "Manual reminder"} ? {item.status.replaceAll("_", " ")}</p><p className="mt-1 text-xs text-slate-500">{new Date(item.scheduled_at).toLocaleString()} ? {item.automatic ? "Automatic" : "Manual"}{item.automatic && item.platform === "youtube" ? ` ? ${item.privacy}` : ""}</p></div>
            <div className="flex flex-wrap gap-2">{item.post_url && <a href={item.post_url} target="_blank" rel="noreferrer" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">View post</a>}
                {item.automatic && <button disabled={busy} onClick={() => action(async () => { const result = await getPostingEvents(item.id); setEvents(current => ({ ...current, [item.id]: result.events })); })} className="rounded-lg border px-3 py-2 text-sm">Posting history</button>}
                {item.status === "scheduled" && <button disabled={busy} onClick={() => action(async () => { await updateSchedule(item.id, { status: "cancelled" }); await load(); })} className="rounded-lg border px-3 py-2 text-sm">Cancel</button>}
                {!item.automatic && <>{!["published", "cancelled"].includes(item.status) && <button disabled={busy} onClick={() => action(async () => { await updateSchedule(item.id, { status: "published" }); await load(); })} className="rounded-lg bg-emerald-100 px-3 py-2 text-sm text-emerald-700">Mark published</button>}<button disabled={busy} onClick={() => action(async () => { await deleteSchedule(item.id); await load(); })} className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">Delete reminder</button></>}
            </div></div>
            {item.error_message && <p role="alert" className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">{item.error_message}</p>}
            {item.remote_post_id && <p className="text-xs text-slate-500">Platform post ID: {item.remote_post_id}</p>}
            {item.media?.length > 0 && <p className="text-xs text-slate-500">Media: {item.media.map(asset => asset.name).join(", ")}</p>}
            {events[item.id] && <ol className="space-y-2 border-t pt-3">{events[item.id].map(event => <li key={event.id} className="text-sm"><span className="text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</span><p>{event.message}</p></li>)}</ol>}
        </article>)}</div>
    </div>;
}
