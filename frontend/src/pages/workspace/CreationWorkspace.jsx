import { useContext, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowRight, Check, LoaderCircle, Save, Workflow } from "lucide-react";
import { AuthContext } from "../../context/AuthContext";
import { useProject } from "../../context/ProjectContext";
import { useBrand } from "../../context/BrandContext";
import { useNiches } from "../../context/NicheContext";
import { generateContent } from "../../api/ai";
import { getProjectContents } from "../../api/content";
import { getProjectMedia } from "../../api/media";
import { getProjectVoices } from "../../api/voice";
import ContentFinisher from "../ai/ContentFinisher";
import BriefStep from "./BriefStep";
import ScriptStep from "./ScriptStep";
import MediaStep from "./MediaStep";
import VoiceStep from "./VoiceStep";
import ScheduleStep from "./ScheduleStep";
import { INITIAL_BRIEF, FORMATS, STEPS, assertSuccess, errorMessage, generationPayload, restoreDraft, staleVoiceScenes } from "./workflow";
import { loadWorkspaceContent, saveWorkspaceContent } from "./workspaceApi";

function readSession(key) {
    try {
        const saved = JSON.parse(localStorage.getItem(key) || "null");
        if (saved?.version !== 1) return {};
        if (!FORMATS[saved.brief?.platform]?.includes(saved.brief?.format)) saved.brief = INITIAL_BRIEF;
        return saved;
    } catch { return {}; }
}

export default function CreationWorkspace() {
    const { user } = useContext(AuthContext);
    if (!user?.id) return <p className="rounded-xl bg-amber-50 p-4">Your profile is unavailable. <Link to="/login" className="underline">Sign in again</Link> to open the workspace.</p>;
    return <Workspace key={user.id} storageKey={`viralforge:creation-workspace:v1:${user.id}`} />;
}

function Workspace({ storageKey }) {
    const { projects } = useProject();
    const { brands } = useBrand();
    const { niches } = useNiches();
    const [cached] = useState(() => readSession(storageKey));
    const [brief, setBrief] = useState({ ...INITIAL_BRIEF, ...cached.brief });
    const [content, setContent] = useState(null);
    const [step, setStep] = useState(0);
    const [dirty, setDirty] = useState(false);
    const [busy, setBusy] = useState("");
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [restoring, setRestoring] = useState(true);
    const [restoreFailed, setRestoreFailed] = useState(false);
    const [exportBusy, setExportBusy] = useState(false);
    const [storageError, setStorageError] = useState(false);
    const [media, setMedia] = useState([]);
    const [voices, setVoices] = useState([]);
    const [savedItems, setSavedItems] = useState([]);
    const [resumeId, setResumeId] = useState("");
    const [listVersion, setListVersion] = useState(0);
    const lock = useRef(false);
    const isBusy = Boolean(busy || restoring || exportBusy);
    const selectedProject = projects.find((item) => Number(item.id) === Number(brief.projectId));
    const brand = brands.find((item) => Number(item.id) === Number(selectedProject?.brand_id));

    useEffect(() => {
        let active = true;
        async function restore() {
            try {
                if (!cached.contentId) return;
                const current = await loadWorkspaceContent(cached.contentId);
                const [assets, audio] = await Promise.all([getProjectMedia(current.project_id), getProjectVoices(current.project_id)]);
                if (!active) return;
                setContent(cached.dirty ? restoreDraft(current, cached.draft) : current);
                setDirty(Boolean(cached.dirty));
                setMedia(assets.media || []); setVoices(audio.voices || []);
                setStep(cached.dirty ? 1 : Math.min(STEPS.length - 1, Math.max(1, Number(cached.step) || 1)));
                setNotice(cached.dirty ? "Restored your local edits. Review and save them before exporting." : "Resumed your saved content.");
            } catch (err) { if (active) { setError(errorMessage(err)); setRestoreFailed(true); } }
            finally { if (active) setRestoring(false); }
        }
        restore();
        return () => { active = false; };
    }, [cached]);

    useEffect(() => {
        if (restoring || restoreFailed) return;
        try {
            localStorage.setItem(storageKey, JSON.stringify({ version: 1, brief, contentId: content?.id, step, dirty, draft: dirty ? content : null }));
            setStorageError(false);
        } catch { setStorageError(true); }
    }, [brief, content, step, dirty, restoring, restoreFailed, storageKey]);

    useEffect(() => {
        let active = true;
        setSavedItems([]); setResumeId("");
        if (brief.projectId) getProjectContents(brief.projectId).then((result) => { if (active) setSavedItems(result.contents || []); }).catch((err) => { if (active) setError(errorMessage(err)); });
        return () => { active = false; };
    }, [brief.projectId, listVersion]);

    useEffect(() => {
        const warn = (event) => { if (busy || exportBusy || (dirty && storageError)) { event.preventDefault(); event.returnValue = ""; } };
        window.addEventListener("beforeunload", warn);
        return () => window.removeEventListener("beforeunload", warn);
    }, [busy, exportBusy, dirty, storageError]);

    const run = async (label, task) => {
        if (lock.current || exportBusy) return;
        lock.current = true; setBusy(label); setError(""); setNotice("");
        try { return await task(); }
        catch (err) { setError(errorMessage(err)); return null; }
        finally { lock.current = false; setBusy(""); }
    };
    const load = async (id) => {
        const current = await loadWorkspaceContent(id);
        const [assets, audio] = await Promise.all([getProjectMedia(current.project_id), getProjectVoices(current.project_id)]);
        setContent(current); setDirty(false); setMedia(assets.media || []); setVoices(audio.voices || []); setRestoreFailed(false);
        return current;
    };
    const refresh = () => load(content.id);
    const refreshVoices = async () => { const result = await getProjectVoices(content.project_id); setVoices(result.voices || []); };
    const save = async () => {
        if (!dirty || !content) return content;
        const saved = await saveWorkspaceContent(content);
        setContent(saved); setDirty(false); setListVersion((value) => value + 1);
        return saved;
    };
    const navigate = (target) => run("Saving your progress...", async () => {
        const current = await save();
        if (target > 0 && !current) throw new Error("Generate content or resume a saved item first.");
        if (target >= 4 && current.scenes.some((scene) => !scene.media_url)) throw new Error("Choose media for every scene before exporting. Open the Media step to fill missing scenes.");
        if (target === 4 && current.generation_config?.audio?.voice_enabled !== false && staleVoiceScenes(current, voices).length) throw new Error("Some narration no longer matches your script. Regenerate those voices in the Voice step first.");
        setStep(target);
    });
    const edit = (next) => { setContent(next); setDirty(true); setNotice(""); };
    const generate = () => run("Generating your content and scene media. Keep this workspace open...", async () => {
        const payload = generationPayload(brief);
        if (!projects.some((item) => Number(item.id) === payload.project_id)) throw new Error("This project is unavailable. Choose another project.");
        await save();
        const result = assertSuccess(await generateContent(payload));
        if (!result.content_id) throw new Error("Generation returned no saved content. Check History before retrying.");
        // Keep the ID recoverable even if a later media/voice lookup fails.
        try { localStorage.setItem(storageKey, JSON.stringify({ version: 1, brief, contentId: result.content_id, step: 1, dirty: false })); } catch { setStorageError(true); }
        await load(result.content_id); setStep(1); setListVersion((value) => value + 1);
        setNotice("Generated and saved. Review the script before continuing.");
    });

    return <div className="mx-auto max-w-6xl space-y-6 pb-12">
        <header className="flex flex-wrap items-start justify-between gap-4">
            <div><p className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-indigo-600"><Workflow size={16} /> Guided creation</p><h1 className="mt-2 text-3xl font-bold text-slate-900">Creation Workspace</h1><p className="mt-2 text-sm text-slate-500">One place to take an idea from brief to export.</p></div>
            <span className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600">{dirty ? "Local edits · not yet saved to project" : content ? "Script saved" : "Brief saved in this browser"}</span>
        </header>

        <div className="flex flex-wrap items-end gap-3 rounded-2xl border border-slate-200 bg-white p-4">
            <label className="min-w-0 flex-1 text-xs font-semibold text-slate-600">Resume saved content in the selected project<select disabled={isBusy} value={resumeId} onChange={(e) => setResumeId(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white p-3 text-sm"><option value="">{brief.projectId ? "Choose a saved item" : "Choose a project in Brief first"}</option>{savedItems.map((item) => <option key={item.id} value={item.id}>{item.title} · {item.content_type}</option>)}</select></label>
            <button type="button" disabled={isBusy || !resumeId} onClick={() => run("Opening saved content...", async () => { await save(); await load(Number(resumeId)); setStep(1); setNotice("Saved content opened in the workspace."); })} className="rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">Resume</button>
            {content && <button type="button" disabled={isBusy} onClick={() => navigate(0)} className="rounded-xl border border-slate-300 px-4 py-3 text-sm">New brief</button>}
        </div>

        <nav aria-label="Creation steps" className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">{STEPS.map((label, index) => <button type="button" key={label} aria-current={step === index ? "step" : undefined} disabled={isBusy || (index > 0 && !content)} onClick={() => navigate(index)} className={`flex items-center gap-2 rounded-xl border px-3 py-3 text-left text-sm font-semibold transition disabled:opacity-40 ${step === index ? "border-indigo-600 bg-indigo-600 text-white" : "border-slate-200 bg-white text-slate-600"}`}><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5 text-xs">{index < step ? <Check size={13} /> : index + 1}</span>{label}</button>)}</nav>
        {content && <div className="flex flex-wrap justify-between gap-2 text-sm text-slate-600"><span className="font-semibold">{content.title} · {content.platform} {content.content_type}</span><Link className="text-indigo-600 underline" to={`/content/${content.id}/edit`}>Open standard editor</Link></div>}
        {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">{notice}</p>}
        {storageError && <p role="alert" className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">Browser draft storage is unavailable. Save your draft before leaving.</p>}
        {restoreFailed && <p className="text-sm text-amber-700">Your previous local draft has been kept. Refresh to retry restoring it, or resume a saved item.</p>}
        {isBusy && <p role="status" className="flex items-center gap-2 rounded-xl bg-indigo-50 p-4 text-sm text-indigo-800"><LoaderCircle size={17} className="animate-spin" />{busy || (exportBusy ? "Preparing your export..." : "Restoring workspace...")}</p>}

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
            <section hidden={step !== 0}><BriefStep brief={brief} onChange={setBrief} projects={projects} niches={niches} brand={brand} busy={isBusy} hasContent={Boolean(content)} onGenerate={generate} /></section>
            {content && <>
                <section hidden={step !== 1}><ScriptStep content={content} onChange={edit} busy={isBusy} /></section>
                <section hidden={step !== 2}><MediaStep content={content} media={media} busy={isBusy} run={run} refresh={refresh} /></section>
                <section hidden={step !== 3}><VoiceStep key={content.id} content={content} voices={voices} busy={isBusy} run={run} refreshVoices={refreshVoices} refresh={refresh} /></section>
                <section hidden={step !== 4}><h2 className="text-xl font-bold">Preview, style and export</h2><p className="mt-1 text-sm text-slate-500">Choose a design, adjust your overlays, then export images or merge a video. Keep this workspace open until the export finishes.</p><fieldset disabled={Boolean(busy || restoring)}><ContentFinisher key={content.id} content={content} projectId={content.project_id} onBusyChange={setExportBusy} disableBackgroundMusic /></fieldset></section>
                <section hidden={step !== 5}><ScheduleStep key={content.id} content={content} busy={isBusy} run={run} refresh={refresh} /></section>
            </>}
        </div>
        {content && <footer className="flex flex-wrap justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4">
            <button type="button" disabled={isBusy || step === 0} onClick={() => navigate(step - 1)} className="inline-flex items-center gap-2 rounded-xl border px-4 py-3 text-sm disabled:opacity-40"><ArrowLeft size={16} />Back</button>
            <div className="flex flex-wrap gap-3"><button type="button" disabled={isBusy || !dirty} onClick={() => run("Saving draft...", async () => { await save(); setNotice("Draft saved to your project."); })} className="inline-flex items-center gap-2 rounded-xl border px-4 py-3 text-sm disabled:opacity-40"><Save size={16} />Save draft</button>{step < STEPS.length - 1 && <button type="button" disabled={isBusy} onClick={() => navigate(step + 1)} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-40">Continue to {STEPS[step + 1]}<ArrowRight size={16} /></button>}</div>
        </footer>}
    </div>;
}
