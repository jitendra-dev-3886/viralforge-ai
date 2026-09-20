import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Archive, Check, Download, File, Film, Image, LoaderCircle, Music, RefreshCw, Search, X } from "lucide-react";
import { deleteMedia, downloadMedia, getAllMedia } from "../../api/media";
import { assetUrl } from "../../api/axios";
import { useProject } from "../../context/ProjectContext";
import DeleteButton from "../../components/DeleteButton";

const TYPES = { final: "Final videos", render: "Scene renders", image: "Images", video: "Videos", audio: "Voice & audio", music: "Music" };
const sizeLabel = (bytes) => !Number.isFinite(Number(bytes)) || Number(bytes) <= 0 ? "Size unavailable" : Number(bytes) < 1048576 ? `${(Number(bytes) / 1024).toFixed(0)} KB` : `${(Number(bytes) / 1048576).toFixed(1)} MB`;
const dateLabel = (value) => value && !Number.isNaN(Date.parse(value)) ? new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : "Date unavailable";
const isReady = (item) => !["pending", "processing", "generating", "failed", "error"].includes(String(item.status).toLowerCase());

export default function ExportPage() {
    const { projects } = useProject();
    const [media, setMedia] = useState([]);
    const [selected, setSelected] = useState([]);
    const [loading, setLoading] = useState(true);
    const [revision, setRevision] = useState(0);
    const [loadError, setLoadError] = useState("");
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [downloading, setDownloading] = useState(false);
    const downloadLock = useRef(false);
    const selectAll = useRef(null);
    const [search, setSearch] = useState("");
    const [project, setProject] = useState("");
    const [type, setType] = useState("");
    const [sort, setSort] = useState("newest");
    const [page, setPage] = useState(1);
    const pageSize = 12;

    useEffect(() => {
        let active = true;
        setLoading(true);
        setLoadError("");
        getAllMedia().then((result) => {
            if (!result.success) throw new Error(result.message || "Unable to load exports.");
            if (!active) return;
            const items = (result.media || []).filter((item) => TYPES[item.media_type]);
            setMedia(items);
            setSelected((ids) => ids.filter((id) => items.some((item) => item.id === id && isReady(item))));
        }).catch((err) => { if (active) setLoadError(err.message || "Unable to load exports."); })
            .finally(() => { if (active) setLoading(false); });
        return () => { active = false; };
    }, [revision]);

    const projectNames = useMemo(() => new Map(projects.map((item) => [String(item.id), item.title])), [projects]);
    const projectOptions = useMemo(() => [...new Set(media.map((item) => String(item.project_id)))].map((id) => ({ id, name: projectNames.get(id) || `Project ${id}` })), [media, projectNames]);
    const filtered = useMemo(() => media.filter((item) => (!project || String(item.project_id) === project) && (!type || item.media_type === type) && `${item.title || ""} ${item.file_name || ""}`.toLowerCase().includes(search.trim().toLowerCase())).sort((a, b) => sort === "name" ? (a.title || a.file_name || "").localeCompare(b.title || b.file_name || "") : sort === "size" ? (b.file_size || 0) - (a.file_size || 0) : (Date.parse(b.created_at) || 0) - (Date.parse(a.created_at) || 0)), [media, project, type, search, sort]);
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    const currentPage = Math.min(page, pageCount);
    const visible = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);
    const selectable = visible.filter(isReady).map((item) => item.id);
    const selectedOnPage = selectable.filter((id) => selected.includes(id)).length;
    const allChecked = selectable.length > 0 && selectedOnPage === selectable.length;
    useEffect(() => { if (selectAll.current) selectAll.current.indeterminate = selectedOnPage > 0 && !allChecked; }, [selectedOnPage, allChecked]);
    const resetSelection = (setter) => (event) => { setter(event.target.value); setPage(1); setSelected([]); setNotice(""); };
    const clearFilters = () => { setSearch(""); setProject(""); setType(""); setPage(1); setSelected([]); };
    const download = async (ids) => {
        if (downloadLock.current || !ids.length) return;
        if (ids.length > 50) { setError("Select up to 50 files per download. Clear the selection and download in smaller batches."); return; }
        downloadLock.current = true;
        setDownloading(true); setError(""); setNotice("");
        try { await downloadMedia(ids); setNotice(`Download started for ${ids.length} ${ids.length === 1 ? "file" : "files"}.`); }
        catch (err) { setError(err.message || "Download failed. Please try again."); }
        finally { downloadLock.current = false; setDownloading(false); }
    };
    const remove = (id) => { setMedia((items) => items.filter((item) => item.id !== id)); setSelected((ids) => ids.filter((value) => value !== id)); setNotice("File removed from your export library."); };
    const fieldClass = "w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200";

    return <div className="mx-auto max-w-7xl p-1 sm:p-4 lg:p-8">
        <header className="mb-7 flex flex-wrap items-center justify-between gap-4"><div><p className="mb-2 text-xs font-semibold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">Your content, ready to go</p><h1 className="text-3xl font-bold">Export Center</h1><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Find, preview, and download your final videos and creative assets.</p></div><div className="flex gap-2"><button disabled={loading || downloading} onClick={() => setRevision((value) => value + 1)} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm disabled:opacity-50 dark:border-slate-700"><RefreshCw size={16} className={loading ? "animate-spin" : ""}/>Refresh</button><Link to="/render" className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700">Create render</Link></div></header>
        <div className="mb-6 grid grid-cols-3 gap-3">{[["Files in library", media.length, File], ["Final videos", media.filter((item) => item.media_type === "final").length, Film], ["Selected files", selected.length, Check]].map(([label, count, Icon]) => <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"><Icon size={18} className="mb-3 text-indigo-500"/><p className="text-2xl font-semibold">{loading || loadError ? "—" : count}</p><p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{label}</p></div>)}</div>
        <div className="mb-5 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 md:grid-cols-4 dark:border-slate-800 dark:bg-slate-900"><label className="relative"><span className="sr-only">Search files</span><Search size={17} className="pointer-events-none absolute left-3 top-3 text-slate-400"/><input value={search} onChange={resetSelection(setSearch)} placeholder="Search title or filename" className={`${fieldClass} pl-9`}/></label><select aria-label="Filter by project" value={project} onChange={resetSelection(setProject)} className={fieldClass}><option value="">All projects</option>{projectOptions.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><select aria-label="Filter by file type" value={type} onChange={resetSelection(setType)} className={fieldClass}><option value="">All file types</option>{Object.entries(TYPES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><select aria-label="Sort files" value={sort} onChange={resetSelection(setSort)} className={fieldClass}><option value="newest">Newest first</option><option value="name">Name A–Z</option><option value="size">Largest first</option></select></div>
        {error && <p role="alert" className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{notice}</p>}
        {loading ? <div role="status" className="flex justify-center gap-3 py-20 text-slate-500"><LoaderCircle className="animate-spin"/>Loading your export library…</div> : loadError ? <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-8 text-center text-red-700"><p>{loadError}</p><button onClick={() => setRevision((value) => value + 1)} className="mt-4 rounded-lg border border-red-300 px-4 py-2">Try again</button></div> : <>
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3"><label className="flex items-center gap-2 text-sm"><input ref={selectAll} type="checkbox" checked={allChecked} disabled={!selectable.length || downloading} onChange={() => setSelected((ids) => allChecked ? ids.filter((id) => !selectable.includes(id)) : [...new Set([...ids, ...selectable])])} className="h-4 w-4 accent-indigo-600"/>Select this page <span className="text-slate-500">({filtered.length} files)</span></label>{(search || project || type) && <button onClick={clearFilters} className="inline-flex items-center gap-1 text-sm text-indigo-600 dark:text-indigo-400"><X size={14}/>Clear filters</button>}</div>
            {selected.length > 0 && <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-900 p-4 text-white"><div><p className="text-sm font-semibold">{selected.length} selected across pages</p><p className="mt-1 text-xs text-slate-300">{selected.length === 1 ? "Download the original file." : "Download all selected files together in a ZIP."}</p></div><div className="flex items-center gap-3"><button disabled={downloading} onClick={() => setSelected([])} className="text-xs text-slate-300 disabled:opacity-50">Clear selection</button><button disabled={downloading} onClick={() => download(selected)} className="inline-flex items-center gap-2 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold disabled:opacity-50">{downloading ? <LoaderCircle size={16} className="animate-spin"/> : <Archive size={16}/>} {downloading ? "Preparing…" : selected.length > 1 ? "Download ZIP" : "Download file"}</button></div></div>}
            {!filtered.length ? <div className="rounded-2xl border border-dashed border-slate-300 py-16 text-center dark:border-slate-700"><Archive size={36} className="mx-auto mb-4 text-slate-400"/><h2 className="text-lg font-semibold">{media.length ? "No matching files" : "Your exports will appear here"}</h2><p className="mt-2 text-sm text-slate-500">{media.length ? "Try another search, project, or file type." : "Generate media or render a video to start your library."}</p></div> : <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{visible.map((item) => <article key={item.id} className={`min-w-0 overflow-hidden rounded-2xl border bg-white dark:bg-slate-900 ${selected.includes(item.id) ? "border-indigo-500 ring-1 ring-indigo-500" : "border-slate-200 dark:border-slate-800"}`}>
                <MediaPreview item={item}/><div className="p-4"><div className="mb-3 flex items-center justify-between gap-2"><span className="rounded-md bg-indigo-50 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">{TYPES[item.media_type]}</span><span className={`text-xs ${isReady(item) ? "text-slate-500" : "text-amber-700"}`}>{item.status || "Available"}</span></div><label className="flex items-start gap-2"><input type="checkbox" checked={selected.includes(item.id)} disabled={downloading || !isReady(item)} onChange={() => setSelected((ids) => ids.includes(item.id) ? ids.filter((id) => id !== item.id) : [...ids, item.id])} className="mt-1 h-4 w-4 shrink-0 accent-indigo-600"/><span className="break-words text-sm font-semibold">{item.title || item.file_name || `File ${item.id}`}</span></label><p className="mt-2 truncate text-xs text-slate-500" title={projectNames.get(String(item.project_id))}>{projectNames.get(String(item.project_id)) || `Project ${item.project_id}`}</p><div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500 dark:text-slate-400"><span>{sizeLabel(item.file_size)}</span>{item.width > 0 && item.height > 0 && <span>{item.width} × {item.height}</span>}{item.duration > 0 && <span>{item.duration}s</span>}<span>{dateLabel(item.created_at)}</span></div><div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-4 dark:border-slate-800"><button disabled={downloading || !isReady(item)} onClick={() => download([item.id])} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"><Download size={15}/>Download</button>{!downloading && <DeleteButton label={item.title || item.file_name || `file ${item.id}`} description="This removes the file from your library and unlinks it from scenes. Existing rendered videos are unchanged." onDelete={() => deleteMedia(item.id)} onDeleted={() => remove(item.id)}/>}</div></div>
            </article>)}</div>}
            {pageCount > 1 && <div className="mt-6 flex items-center justify-between gap-3 text-sm"><span className="text-slate-500">Page {currentPage} of {pageCount}</span><div className="flex gap-2"><button disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)} className="rounded-lg border px-4 py-2 disabled:opacity-40">Previous</button><button disabled={currentPage >= pageCount} onClick={() => setPage(currentPage + 1)} className="rounded-lg border px-4 py-2 disabled:opacity-40">Next</button></div></div>}
        </>}
    </div>;
}

function MediaPreview({ item }) {
    const [failed, setFailed] = useState(false);
    const url = assetUrl(item.file_url);
    const video = item.mime_type?.startsWith("video/") || ["video", "render", "final"].includes(item.media_type);
    const audio = item.mime_type?.startsWith("audio/") || ["audio", "music"].includes(item.media_type);
    const image = item.mime_type?.startsWith("image/") || item.media_type === "image";
    const Icon = video ? Film : audio ? Music : image ? Image : File;
    return <div className="flex h-48 items-center justify-center overflow-hidden bg-slate-100 dark:bg-slate-800">{url && !failed && video ? <video src={url} controls preload="none" onError={() => setFailed(true)} className="h-full w-full bg-black object-contain"/> : url && !failed && image ? <img src={url} alt={item.title || item.file_name || "Export preview"} loading="lazy" onError={() => setFailed(true)} className="h-full w-full object-contain"/> : <div className="w-full px-4 text-center"><Icon className="mx-auto mb-3 text-slate-400" size={32}/>{url && !failed && audio ? <audio src={url} controls preload="none" onError={() => setFailed(true)} className="w-full"/> : <p className="text-xs text-slate-500">Preview unavailable</p>}</div>}</div>;
}
