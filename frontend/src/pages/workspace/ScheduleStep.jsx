import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createSchedule, getSchedules } from "../../api/schedule";
import AutoPostForm from "../settings/AutoPostForm";
import { updateContent } from "../../api/content";
import { assertSuccess, errorMessage } from "./workflow";

export default function ScheduleStep({ content, busy, run, refresh }) {
    const [when, setWhen] = useState("");
    const [scheduled, setScheduled] = useState([]);
    const [error, setError] = useState("");
    const [loaded, setLoaded] = useState(false);
    useEffect(() => {
        let active = true;
        getSchedules().then((result) => { if (active) { setScheduled((result.schedules || []).filter((item) => item.content_id === content.id && item.status === "scheduled")); setLoaded(true); } }).catch((err) => { if (active) setError(errorMessage(err)); });
        return () => { active = false; };
    }, [content.id]);
    return <div className="space-y-5">
        <div><h2 className="text-xl font-bold">Ready to publish?</h2><p className="mt-1 text-sm text-slate-500">Approve your finished content, then schedule automatic posting to a connected account or save a manual reminder.</p></div>
        <div className="rounded-2xl bg-slate-50 p-5"><h3 className="font-semibold">{content.title}</h3><p className="mt-1 text-sm text-slate-600">{content.platform} · {content.content_type} · {content.status}</p><p className="mt-4 whitespace-pre-wrap text-sm">{content.caption}</p></div>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        {scheduled.length > 0 ? <div className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">Already scheduled: {scheduled.map((item) => new Date(item.scheduled_at).toLocaleString()).join(", ")}. <Link to="/scheduler" className="underline">Manage in Scheduler</Link>.</div> : <fieldset disabled={busy} className="space-y-4">
            {content.status !== "approved" && <button type="button" onClick={() => run("Approving content...", async () => { assertSuccess(await updateContent(content.id, { status: "approved" })); await refresh(); })} className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white">Approve this content</button>}
            <label className="block text-sm">Publish date and time ({Intl.DateTimeFormat().resolvedOptions().timeZone})<input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} className="mt-2 block rounded-xl border border-slate-300 p-3" /></label>
            <button type="button" disabled={!loaded || content.status !== "approved" || !when} onClick={() => run("Adding to publishing queue...", async () => {
                const date = new Date(when);
                if (!Number.isFinite(date.getTime()) || date <= new Date()) throw new Error("Choose a future publishing time.");
                const result = assertSuccess(await createSchedule({ project_id: content.project_id, content_id: content.id, platform: content.platform, scheduled_at: date.toISOString(), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone }));
                setScheduled([result.schedule]);
            })} className="rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">Save reminder — publish manually</button>
            <p className="text-xs text-slate-500">A reminder does not publish your content. Use Automatic posting below to publish at the selected time.</p>
        </fieldset>}
        {content.status === "approved" && <AutoPostForm content={content} disabled={busy} onScheduled={async schedule => setScheduled(current => [...current, schedule])} />}
        <Link to="/scheduler" className="inline-block text-sm font-semibold text-indigo-600 underline">Open posting history</Link>
        <Link to="/export" className="inline-block text-sm font-semibold text-indigo-600 underline">Open Export Center</Link>
    </div>;
}
