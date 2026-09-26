import { useEffect, useRef, useState } from "react";
import { getContent } from "../../api/content";
import ScheduleStep from "../workspace/ScheduleStep";
import { assertSuccess, errorMessage } from "../workspace/workflow";

export default function GeneratedPublishing({ contentId, disabled }) {
    const [content, setContent] = useState(null);
    const [open, setOpen] = useState(false);
    const [busy, setBusy] = useState("");
    const [error, setError] = useState("");
    const lock = useRef(false);
    // Reopen after export/upload to reload saved copy and the latest assets.
    useEffect(() => { if (disabled) setOpen(false); }, [disabled]);

    const refresh = async () => {
        const response = assertSuccess(await getContent(contentId));
        const saved = response.content || response.data || response;
        if (!saved.id || !saved.platform) throw new Error("Saved content is unavailable. Refresh and try again.");
        setContent(saved);
    };
    const run = async (message, action) => {
        if (lock.current || disabled) return;
        lock.current = true;
        setBusy(message); setError("");
        try { await action(); }
        catch (error) { setError(errorMessage(error)); }
        finally { lock.current = false; setBusy(""); }
    };

    return <section className="mt-6 border-t border-slate-200 pt-5">
        <button type="button" disabled={disabled || Boolean(busy)} aria-expanded={open}
            onClick={() => open ? setOpen(false) : run("Loading publishing options...", async () => { await refresh(); setOpen(true); })}
            className="rounded-xl bg-emerald-600 px-5 py-3 font-semibold text-white disabled:opacity-50">
            {open ? "Close scheduling" : "Schedule this post"}
        </button>
        <p className="mt-2 text-sm text-slate-500">Export your finished images or video, then approve and schedule this output.</p>
        {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
        {busy && <p role="status" className="mt-3 text-sm text-indigo-700">{busy}</p>}
        {open && content && <div className="mt-5"><ScheduleStep key={content.id} content={content} busy={disabled || Boolean(busy)} run={run} refresh={refresh} /></div>}
    </section>;
}
