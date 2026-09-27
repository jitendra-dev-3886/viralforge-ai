import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api, { assetUrl } from "../../api/axios";
import { apiErrorMessage } from "../../api/errors";
import { getProjects } from "../../api/project";
import { getSocialConnections } from "../../api/social";
import { getProjectMedia } from "../../api/media";
import { uploadProjectMusic } from "../../api/projectRender";
import { useNiches } from "../../context/NicheContext";

const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const initial = () => ({ project_id: "", platform: "instagram", content_type: "Carousel", niche: "", language: "English", style: "Engaging", visual_style: "minimal", scene_count: 5, total_duration: 30, voice: "auto", voice_speed: "+0%", music_id: "", music_volume: 0.18, days: [0, 1, 2, 3, 4, 5, 6], time: "09:00", timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata", lead_minutes: 30, mode: "approval", publishing_account_id: "", privacy: "private", made_for_kids: "", enabled: true });
const inputClass = "mt-1 block w-full rounded-xl border border-slate-200 bg-white p-3 text-sm";
const buttonClass = "rounded-xl border px-4 py-2 text-sm font-semibold disabled:opacity-40";
const timezones = [...new Set(["UTC", "Asia/Kolkata", ...(Intl.supportedValuesOf?.("timeZone") || ["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Dubai", "Asia/Singapore", "Australia/Sydney"])])].sort();

function OptionSelect({ label, value, values, onChange, placeholder, format = value => value }) {
    // Keep saved values selectable when they are outside the usual presets.
    const options = [...new Set([...values, value].filter(item => item !== "" && item != null).map(String))];
    return <label className="text-sm font-medium">{label}<select required className={inputClass} value={value} onChange={event => onChange(event.target.value)}>{placeholder && <option value="">{placeholder}</option>}{options.map(option => <option key={option} value={option}>{format(option)}</option>)}</select></label>;
}

export default function AutoMode() {
    const { niches } = useNiches();
    const [form, setForm] = useState(initial);
    const [editing, setEditing] = useState(null);
    const [projects, setProjects] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [data, setData] = useState({ rules: [], runs: [], worker_enabled: true });
    const [loaded, setLoaded] = useState(false);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [music, setMusic] = useState([]);
    const [musicLoaded, setMusicLoaded] = useState(false);
    const lock = useRef(false);
    const refresh = useCallback(async () => {
        const response = await api.get("/automations/");
        setData(response.data);
    }, []);
    useEffect(() => {
        let active = true;
        setMusic([]); setMusicLoaded(false);
        if (form.project_id) getProjectMedia(form.project_id).then(result => {
            if (!active) return;
            setMusic((result.media || []).filter(item => item.media_type === "music" && item.status === "ready"));
            setMusicLoaded(true);
        }).catch(err => { if (active) setError(apiErrorMessage(err, "Unable to load project music.")); });
        return () => { active = false; };
    }, [form.project_id]);
    useEffect(() => {
        let active = true;
        Promise.all([getProjects(), getSocialConnections(), api.get("/automations/")]).then(([projectData, socialData, automationData]) => {
            if (!active) return;
            setProjects(projectData.projects || []);
            setAccounts(socialData.accounts || []);
            setData(automationData.data);
            setLoaded(true);
        }).catch(err => { if (active) setError(apiErrorMessage(err, "Unable to load Auto Mode.")); });
        const timer = setInterval(() => {
            api.get("/automations/").then(response => { if (active) setData(response.data); }).catch(() => {});
        }, 15000);
        return () => { active = false; clearInterval(timer); };
    }, []);
    const change = (key, value) => setForm(current => ({ ...current, [key]: value }));
    const action = async task => {
        if (lock.current) return;
        lock.current = true;
        setBusy(true); setError(""); setNotice("");
        try { await task(); }
        catch (err) { setError(apiErrorMessage(err, "Unable to save automation.")); }
        finally { lock.current = false; setBusy(false); }
    };
    const save = event => {
        event.preventDefault();
        action(async () => {
            const payload = { ...form, music_id: form.music_id ? Number(form.music_id) : null, music_volume: Number(form.music_volume), project_id: Number(form.project_id), scene_count: Number(form.scene_count), total_duration: Number(form.total_duration), lead_minutes: Number(form.lead_minutes), publishing_account_id: form.publishing_account_id ? Number(form.publishing_account_id) : null, made_for_kids: form.made_for_kids === "" ? null : form.made_for_kids === "yes" };
            if (editing) await api.put(`/automations/${editing}`, payload);
            else await api.post("/automations/", payload);
            setForm(initial()); setEditing(null);
            setNotice("Schedule saved. The next occurrence leaves enough time for content preparation.");
            await refresh();
        });
    };
    const edit = rule => {
        const { id, next_run_at: _nextRunAt, topic: _legacyTopic, ...config } = rule;
        setForm({ ...initial(), ...config, music_id: config.music_id || "", publishing_account_id: config.publishing_account_id || "", made_for_kids: config.made_for_kids == null ? "" : config.made_for_kids ? "yes" : "no" });
        setEditing(id); setNotice(""); setError("");
        window.scrollTo({ top: 0, behavior: "smooth" });
    };
    const video = ["Reel", "Shorts", "Video"].includes(form.content_type);
    const formats = form.platform === "youtube" ? ["Shorts", "Video"] : ["Reel", "Carousel", "Post", "Quote", "Story"];
    const selectedMusic = music.find(track => track.id === Number(form.music_id));
    return <div className="space-y-6 p-1 sm:p-4 lg:p-8">
        <header><h1 className="text-3xl font-bold">Auto Mode</h1><p className="mt-2 text-slate-500">Generate content on a recurring schedule. Give each format its own days, time and publishing choice.</p></header>
        {error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
        {!loaded && !error && <p role="status">Loading Auto Mode...</p>}
        {!data.worker_enabled && <p className="rounded-xl bg-amber-50 p-3 text-sm">Automatic generation is disabled on this server.</p>}
        <form onSubmit={save} className="rounded-2xl bg-white p-5 shadow-sm">
            <fieldset disabled={busy || !loaded} className="space-y-5">
                <h2 className="text-lg font-semibold">{editing ? "Edit schedule" : "New schedule"}</h2>
                <div className="grid gap-4 sm:grid-cols-2">
                    <label className="text-sm font-medium">Project<select required className={inputClass} value={form.project_id} onChange={event => {
                        const project = projects.find(item => item.id === Number(event.target.value));
                        setForm(current => ({ ...current, project_id: event.target.value, music_id: "", niche: project?.niche || "", language: project?.language || "English" }));
                    }}><option value="">Select project</option>{projects.map(project => <option key={project.id} value={project.id}>{project.title}</option>)}</select></label>
                    <label className="text-sm font-medium">Platform<select className={inputClass} value={form.platform} onChange={event => setForm(current => ({ ...current, platform: event.target.value, content_type: event.target.value === "youtube" ? "Shorts" : "Carousel", publishing_account_id: "" }))}>{["instagram", "facebook", "youtube"].map(platform => <option key={platform} value={platform}>{platform === "youtube" ? "YouTube" : platform[0].toUpperCase() + platform.slice(1)}</option>)}</select></label>
                    <label className="text-sm font-medium">Format<select className={inputClass} value={form.content_type} onChange={event => setForm(current => ({ ...current, content_type: event.target.value, ...(event.target.value === "Story" ? { mode: "approval" } : {}), scene_count: event.target.value === "Carousel" ? Math.max(3, current.scene_count) : current.scene_count }))}>{formats.map(format => <option key={format}>{format}</option>)}</select></label>
                    <OptionSelect label="Niche" value={form.niche} values={niches.map(niche => niche.name)} placeholder="Select niche" onChange={value => change("niche", value)} />
                </div>
                <div className="rounded-xl bg-indigo-50 p-4 text-sm"><p className="font-semibold">Topic: top unused live trend</p><p className="mt-1 text-slate-600">At each run, Auto Mode selects the highest-ranked unused trend for your niche, project and format. It skips the run when no suitable new trend is available.</p></div>
                <div className="grid gap-4 sm:grid-cols-3">
                    <OptionSelect label="Language" value={form.language} values={["English", "Hindi", "Hinglish"]} onChange={value => change("language", value)} />
                    <OptionSelect label="Writing and caption tone" value={form.style} values={["Engaging", "Educational", "Energetic", "Storytelling", "Promotional", "Inspirational", "Funny", "Emotional", "Suspenseful", "Listicle"]} onChange={value => change("style", value)} />
                    <label className="text-sm font-medium">Visual style<select className={inputClass} value={form.visual_style} onChange={event => change("visual_style", event.target.value)}>{["minimal", "bold", "cinematic", "professional", "playful", "scrapbook"].map(style => <option key={style} value={style}>{style[0].toUpperCase() + style.slice(1)}</option>)}</select></label>
                    {!["Post", "Quote"].includes(form.content_type) && <OptionSelect label={form.content_type === "Carousel" ? "Slides" : "Scenes"} value={form.scene_count} values={Array.from({ length: 10 }, (_, index) => index + 1).filter(count => form.content_type !== "Carousel" || count >= 3)} onChange={value => change("scene_count", Number(value))} />}
                    {video && <OptionSelect label="Duration" value={form.total_duration} values={[5, 10, 15, 20, 30, 45, 60, 90, 120, 180]} format={value => `${value} seconds`} onChange={value => change("total_duration", Number(value))} />}
                </div>
                {video && <section className="space-y-4 rounded-xl border border-slate-200 p-4">
                    <h3 className="font-semibold">Voice and music</h3>
                    <div className="grid gap-4 sm:grid-cols-2">
                        <label className="text-sm font-medium">Narration voice<select className={inputClass} value={form.voice} onChange={event => change("voice", event.target.value)}><option value="auto">Automatic (match narration language)</option><option value="off">No narration</option>{[["en-US-AriaNeural", "Aria - English"], ["en-US-GuyNeural", "Guy - English"], ["en-GB-SoniaNeural", "Sonia - English"], ["hi-IN-SwaraNeural", "Swara - Hindi"], ["hi-IN-MadhurNeural", "Madhur - Hindi"]].map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
                        {form.voice !== "off" && <OptionSelect label="Narration pace" value={form.voice_speed} values={["-10%", "-5%", "+0%", "+5%", "+10%"]} format={value => value === "+0%" ? "Normal" : `${value} speed`} onChange={value => change("voice_speed", value)} />}
                        <label className="text-sm font-medium">Background music<select className={inputClass} disabled={!musicLoaded} value={form.music_id || ""} onChange={event => change("music_id", event.target.value)}><option value="">No background music</option>{form.music_id && !selectedMusic && <option value={form.music_id}>{musicLoaded ? "Saved track unavailable - select another" : "Loading saved track..."}</option>}{music.map(track => <option key={track.id} value={track.id}>{track.title || track.file_name}</option>)}</select></label>
                        {form.music_id && <OptionSelect label="Music volume" value={form.music_volume} values={[0.08, 0.12, 0.18, 0.25, 0.35]} format={value => `${Math.round(Number(value) * 100)}%`} onChange={value => change("music_volume", Number(value))} />}
                    </div>
                    {selectedMusic && <audio controls preload="none" src={assetUrl(selectedMusic.file_url)} className="w-full" />}
                    <label className="block text-sm font-medium">Upload a project music track<input type="file" accept=".mp3,.wav,.m4a,.aac,.ogg" disabled={!form.project_id || !musicLoaded} className="mt-2 block w-full text-sm" onChange={event => {
                        const file = event.target.files?.[0];
                        event.target.value = "";
                        if (!file) return;
                        action(async () => {
                            if (file.size > 25 * 1024 * 1024) throw new Error("Music must be 25 MB or smaller.");
                            const result = await uploadProjectMusic(Number(form.project_id), file, true);
                            setMusic(current => [...current, result.music]); setMusicLoaded(true);
                            change("music_id", result.music.id);
                            setNotice("Music uploaded and selected. Save the schedule to use it.");
                        });
                    }} /></label>
                    <p className="text-xs text-slate-500">Narration is generated for every scene before export. Select or upload music once to reuse it on future runs. Voice language follows the narration text; music plays underneath at the selected volume.</p>
                </section>}
                <div><p className="mb-2 text-sm font-medium">Repeat on</p><div className="flex flex-wrap gap-3">{weekdays.map((day, index) => <label key={day} className="flex items-center gap-2 rounded-lg border p-2 text-sm"><input type="checkbox" checked={form.days.includes(index)} onChange={() => change("days", form.days.includes(index) ? form.days.filter(value => value !== index) : [...form.days, index].sort())} />{day}</label>)}</div></div>
                <div className="grid gap-4 sm:grid-cols-3">
                    <fieldset><legend className="text-sm font-medium">{form.mode === "automatic" ? "Posting time" : "Draft ready by"} (24-hour)</legend><div className="flex items-center gap-2"><select aria-label="Hour" className={inputClass} value={form.time.split(":")[0]} onChange={event => change("time", `${event.target.value}:${form.time.split(":")[1]}`)}>{Array.from({ length: 24 }, (_, index) => String(index).padStart(2, "0")).map(hour => <option key={hour}>{hour}</option>)}</select><span aria-hidden="true">:</span><select aria-label="Minute" className={inputClass} value={form.time.split(":")[1]} onChange={event => change("time", `${form.time.split(":")[0]}:${event.target.value}`)}>{Array.from({ length: 60 }, (_, index) => String(index).padStart(2, "0")).map(minute => <option key={minute}>{minute}</option>)}</select></div></fieldset>
                    <OptionSelect label="Timezone" value={form.timezone} values={timezones} format={value => value.replaceAll("_", " ")} onChange={value => change("timezone", value)} />
                    <OptionSelect label="Prepare ahead" value={form.lead_minutes} values={[5, 15, 30, 60, 120, 240, 720, 1440]} format={value => Number(value) % 60 === 0 ? `${Number(value) / 60} hour${Number(value) === 60 ? "" : "s"}` : `${value} minutes`} onChange={value => change("lead_minutes", Number(value))} />
                </div>
                <label className="block text-sm font-medium">After generation<select className={inputClass} value={form.mode} onChange={event => change("mode", event.target.value)}><option value="approval">Save a draft for my approval</option><option value="automatic" disabled={form.content_type === "Story"}>Publish automatically</option></select></label>
                {form.mode === "automatic" && <div className="space-y-4 rounded-xl bg-indigo-50 p-4">
                    <label className="block text-sm font-medium">Connected account<select required className={inputClass} value={form.publishing_account_id} onChange={event => change("publishing_account_id", event.target.value)}><option value="">Select account</option>{accounts.filter(account => account.status === "connected" && account.provider === form.platform).map(account => <option key={account.id} value={account.id}>{account.name}</option>)}</select></label>
                    <Link to="/settings#social-accounts" className="inline-block text-sm text-indigo-700 underline">Manage connected accounts</Link>
                    {form.platform === "youtube" && <div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-medium">YouTube visibility<select className={inputClass} value={form.privacy} onChange={event => change("privacy", event.target.value)}><option value="private">Private upload</option><option value="unlisted">Unlisted</option><option value="public">Public</option></select></label><label className="text-sm font-medium">Made for kids?<select required className={inputClass} value={form.made_for_kids} onChange={event => change("made_for_kids", event.target.value)}><option value="">Choose audience</option><option value="no">No</option><option value="yes">Yes</option></select></label></div>}
                    <p className="text-sm text-indigo-900">Saving this schedule authorizes generation and posting to this account without further approval, using the selected visibility.</p>
                </div>}
                <p className="text-xs leading-5 text-slate-500">Uses your project branding, configured AI providers and normal export allowance. Checks the latest 30 content items for repeated text and visual sources. Your server must stay running. Missed posting times are skipped; failed or repeated content stays for review.</p>
                <div className="flex gap-3"><button disabled={!form.days.length} className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-40">{busy ? "Saving..." : editing ? "Save changes" : "Create schedule"}</button>{editing && <button type="button" className={buttonClass} onClick={() => { setEditing(null); setForm(initial()); }}>Cancel edit</button>}</div>
            </fieldset>
        </form>
        <section className="space-y-3"><h2 className="text-xl font-semibold">Your schedules</h2><p className="text-sm text-slate-500">Pausing stops future generation. Posts already queued remain in <Link className="text-indigo-600 underline" to="/scheduler">Scheduler</Link>, where you can cancel them.</p>
            {loaded && !data.rules.length && <p className="rounded-xl border border-dashed p-6 text-slate-500">Create a schedule for each format and time you want.</p>}
            {data.rules.map(rule => <article key={rule.id} className="flex flex-wrap items-center justify-between gap-4 rounded-2xl bg-white p-5 shadow-sm"><div><h3 className="font-semibold">{rule.content_type} · {rule.platform} · {projects.find(project => project.id === rule.project_id)?.title || `Project #${rule.project_id}`}</h3><p className="mt-1 text-sm">{rule.days.map(day => weekdays[day]).join(", ")} at {rule.time} ({rule.timezone}) · {rule.mode === "automatic" ? "Automatic posting" : "Drafts for approval"}</p><p className="mt-1 text-sm text-slate-500">{rule.enabled ? `Next: ${new Date(rule.next_run_at).toLocaleString(undefined, { timeZone: rule.timezone })} (${rule.timezone})` : "Paused"}</p><p className="mt-1 text-sm text-slate-500">Top unused trend: {rule.niche}</p></div><div className="flex gap-2"><button disabled={busy} onClick={() => edit(rule)} className={buttonClass}>Edit</button><button disabled={busy} onClick={() => action(async () => { await api.patch(`/automations/${rule.id}`, { enabled: !rule.enabled }); await refresh(); })} className={buttonClass}>{rule.enabled ? "Pause" : "Resume"}</button></div></article>)}
        </section>
        <section className="space-y-3"><div className="flex items-center justify-between"><h2 className="text-xl font-semibold">Recent runs</h2><button disabled={busy} className={buttonClass} onClick={() => action(refresh)}>Refresh</button></div>
            {loaded && !data.runs.length && <p className="text-sm text-slate-500">Generated drafts and posting results will appear here.</p>}
            {data.runs.map(run => <article key={run.id} className="space-y-2 rounded-2xl bg-white p-4 shadow-sm"><p className="text-sm font-medium">Schedule #{run.rule_id} · {new Date(run.scheduled_at).toLocaleString()} · {run.status.replaceAll("_", " ")}</p>{run.topic && <p className="text-sm text-slate-700">{run.topic}</p>}{run.error_message && <p className="text-sm text-amber-700">{run.error_message}</p>}<div className="flex flex-wrap gap-4 text-sm">{run.content_id && <Link className="text-indigo-600 underline" to={`/content/${run.content_id}/edit`}>Review content</Link>}{run.content_id && <Link className="text-indigo-600 underline" to="/scheduler">{run.schedule_id ? "View posting record" : "Approve and schedule"}</Link>}</div></article>)}
        </section>
    </div>;
}
