import { useEffect, useMemo, useState } from "react";
import { ChevronDown, ChevronUp, History, LoaderCircle, Search } from "lucide-react";
import { Link } from "react-router-dom";

import { deleteContent, getAllContents } from "../../api/content";
import DeleteButton from "../../components/DeleteButton";
import { useProject } from "../../context/ProjectContext";
import PreviewPanel from "../ai/PreviewPanel";

const CONTENT_TYPES = ["Reel", "Carousel", "Story", "Post", "Quote", "Shorts", "Long Video", "Community Post"];
const PLATFORMS = ["Instagram", "Facebook", "YouTube"];

export default function HistoryPage() {
  const { projects } = useProject();
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({ search: "", project_id: "", platform: "", content_type: "" });
  const query = useMemo(() => Object.fromEntries(Object.entries(filters).filter(([, value]) => String(value).trim())), [filters]);

  useEffect(() => {
    let active = true;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        setError("");
        const response = await getAllContents(query);
        if (active) setContents(response.contents || []);
      } catch (requestError) {
        if (active) setError(requestError.response?.data?.detail || "Could not load content history.");
      } finally {
        if (active) setLoading(false);
      }
    }, filters.search ? 300 : 0);
    return () => { active = false; clearTimeout(timer); };
  }, [query, filters.search]);

  const updateFilter = (event) => { setPage(1); setFilters((current) => ({ ...current, [event.target.name]: event.target.value })); };
  const pageCount = Math.max(1, Math.ceil(contents.length / pageSize));
  const visibleContents = contents.slice((Math.min(page, pageCount) - 1) * pageSize, Math.min(page, pageCount) * pageSize);

  return (
    <div className="p-1 sm:p-4 lg:p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div><h1 className="text-3xl font-bold">History</h1><p className="mt-2 text-slate-500">Review every database-saved generation and its media.</p></div>
        <Link to="/ai-studio" className="inline-flex items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-white hover:bg-blue-700">Generate New Content</Link>
      </div>

      <div className="mb-4 flex justify-end"><select value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }} className="rounded-xl border px-3 py-2 text-sm"><option value="10">10 per page</option><option value="25">25 per page</option><option value="50">50 per page</option></select></div>

      <div className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-5">
        <label className="relative md:col-span-2"><Search className="absolute left-3 top-3 text-slate-400" size={18} /><input name="search" value={filters.search} onChange={updateFilter} placeholder="Search title or caption" className="w-full rounded-xl border border-slate-300 py-2.5 pl-10 pr-3" /></label>
        <select name="project_id" value={filters.project_id} onChange={updateFilter} className="rounded-xl border border-slate-300 px-3 py-2.5"><option value="">All projects</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}</select>
        <select name="platform" value={filters.platform} onChange={updateFilter} className="rounded-xl border border-slate-300 px-3 py-2.5"><option value="">All platforms</option>{PLATFORMS.map((item) => <option key={item}>{item}</option>)}</select>
        <select name="content_type" value={filters.content_type} onChange={updateFilter} className="rounded-xl border border-slate-300 px-3 py-2.5"><option value="">All formats</option>{CONTENT_TYPES.map((item) => <option key={item}>{item}</option>)}</select>
      </div>

      {error && <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">{String(error)}</div>}
      {loading && <div className="flex items-center justify-center gap-3 rounded-3xl bg-white p-6 text-slate-500 sm:p-12"><LoaderCircle className="animate-spin" /> Loading history…</div>}
      {!loading && !error && contents.length === 0 && <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-center sm:p-12"><History className="mx-auto text-slate-400" size={48} /><h2 className="mt-4 text-2xl font-semibold">No matching history</h2><p className="mt-2 text-slate-500">Generate content or change the filters.</p></div>}

      {!loading && <div className="space-y-4">{visibleContents.map((content) => {
        const expanded = expandedId === content.id;
        return <article key={content.id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center gap-2"><button type="button" onClick={() => setExpandedId(expanded ? null : content.id)} className="flex flex-1 items-center justify-between gap-4 p-5 text-left">
            <div><div className="flex flex-wrap items-center gap-2"><h2 className="font-semibold text-slate-900">{content.title}</h2><span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs text-blue-700">{content.content_type}</span><span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{content.platform}</span></div><p className="mt-2 text-sm text-slate-500">{content.project_title || `Project ${content.project_id}`} · {new Date(content.created_at).toLocaleString()} · {(content.scenes || []).length} scene{content.scenes?.length === 1 ? "" : "s"}</p></div>
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </button><div className="mr-4 flex flex-wrap items-center gap-2"><Link to={`/content/${content.id}/edit`} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white">Edit</Link><DeleteButton label={content.title || `content ${content.id}`} description="This deletes the content and its associated scenes, voice records, and image records." onDelete={() => deleteContent(content.id)} onDeleted={() => { setContents((items) => items.filter((item) => item.id !== content.id)); setExpandedId((id) => id === content.id ? null : id); }} /></div></div>
          {expanded && <div className="border-t border-slate-200 bg-slate-50 p-4"><PreviewPanel data={{ success: true, content_id: content.id, data: content }} username={content.branding?.username} logo={content.branding?.logo} /></div>}
        </article>;
      })}</div>}
      {!loading && contents.length > pageSize && <div className="mt-5 flex items-center justify-between text-sm text-slate-500"><span>{contents.length} records</span><div className="flex items-center gap-2"><button disabled={page<=1} onClick={()=>setPage(value=>value-1)} className="rounded-lg border px-3 py-2 disabled:opacity-40">Previous</button><span>{Math.min(page,pageCount)} / {pageCount}</span><button disabled={page>=pageCount} onClick={()=>setPage(value=>value+1)} className="rounded-lg border px-3 py-2 disabled:opacity-40">Next</button></div></div>}
    </div>
  );
}
