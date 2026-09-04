import { useEffect, useState } from "react";
import { Download, LoaderCircle } from "lucide-react";
import { useProject } from "../../context/ProjectContext";
import { downloadSceneMedia, getProjectScenes } from "../../api/scene";

export default function DownloaderPage() {
  const { projects } = useProject();
  const [projectId, setProjectId] = useState("");
  const [scenes, setScenes] = useState([]);
  const [busy, setBusy] = useState(null);
  const [message, setMessage] = useState("");
  useEffect(() => { if (!projectId && projects[0]) setProjectId(projects[0].id); }, [projects, projectId]);
  const load = async () => { if (projectId) setScenes((await getProjectScenes(projectId)).scenes || []); };
  useEffect(() => { load().catch(() => setMessage("Unable to load scenes.")); }, [projectId]);
  const download = async (id) => { try { setBusy(id); setMessage(""); await downloadSceneMedia(id); await load(); setMessage("Scene media is ready."); } catch (error) { setMessage(error.response?.data?.detail || "Media download failed."); } finally { setBusy(null); } };
  return <div className="p-1 sm:p-4 lg:p-8"><h1 className="text-3xl font-bold">Downloader</h1><p className="mt-2 text-slate-500">Download or retry stock media for each project scene.</p>
    <select value={projectId} onChange={(e) => setProjectId(Number(e.target.value))} className="mt-6 w-full max-w-xl rounded-xl border p-3"><option value="">Select project</option>{projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}</select>
    {message && <p className="mt-4 rounded-xl bg-blue-50 p-3 text-sm text-blue-700">{message}</p>}
    <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{scenes.map(scene => <article key={scene.id} className="rounded-2xl border bg-white p-5 shadow-sm"><div className="flex justify-between gap-3"><strong>Scene {scene.scene_number}</strong><span className="text-xs capitalize text-slate-500">{scene.status}</span></div><p className="mt-2 line-clamp-2 text-sm text-slate-600">{scene.text}</p><p className="mt-2 text-xs text-slate-400">{scene.media_type} · {scene.keyword}</p><button onClick={() => download(scene.id)} disabled={busy === scene.id} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-50">{busy === scene.id ? <LoaderCircle className="animate-spin" size={16}/> : <Download size={16}/>} {scene.media_id ? "Verify media" : "Download media"}</button></article>)}</div>
  </div>;
}
