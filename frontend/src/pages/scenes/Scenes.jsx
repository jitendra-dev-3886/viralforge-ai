import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { useProject } from "../../context/ProjectContext";
import { getProjectScenes, updateScene } from "../../api/scene";

export default function ScenesPage() {
  const { projects } = useProject(); const [projectId,setProjectId]=useState(""); const [scenes,setScenes]=useState([]); const [saving,setSaving]=useState(null);
  useEffect(()=>{if(!projectId&&projects[0])setProjectId(projects[0].id)},[projects,projectId]);
  useEffect(()=>{if(projectId)getProjectScenes(projectId).then(r=>setScenes(r.scenes||[]))},[projectId]);
  const change=(id,key,value)=>setScenes(items=>items.map(item=>item.id===id?{...item,[key]:value}:item));
  const save=async(scene)=>{setSaving(scene.id); await updateScene(scene.id,{text:scene.text,keyword:scene.keyword,duration:Number(scene.duration)}); setSaving(null);};
  return <div className="p-1 sm:p-4 lg:p-8"><h1 className="text-3xl font-bold">Scenes</h1><p className="mt-2 text-slate-500">Review and edit scenes within a project.</p><select value={projectId} onChange={e=>setProjectId(Number(e.target.value))} className="mt-6 w-full max-w-xl rounded-xl border p-3"><option value="">Select project</option>{projects.map(p=><option key={p.id} value={p.id}>{p.title}</option>)}</select><div className="mt-6 space-y-4">{scenes.map(scene=><article key={scene.id} className="rounded-2xl border bg-white p-5 shadow-sm"><div className="mb-4 flex flex-wrap justify-between gap-2"><strong>Scene {scene.scene_number}</strong><span className="text-sm capitalize text-slate-500">{scene.media_type} · {scene.status}</span></div><textarea value={scene.text||""} onChange={e=>change(scene.id,"text",e.target.value)} rows={3} className="w-full rounded-xl border p-3"/><div className="mt-3 grid gap-3 sm:grid-cols-[1fr_8rem]"><input value={scene.keyword||""} onChange={e=>change(scene.id,"keyword",e.target.value)} placeholder="Media keyword" className="rounded-xl border p-3"/><input type="number" min="1" value={scene.duration||5} onChange={e=>change(scene.id,"duration",e.target.value)} className="rounded-xl border p-3"/></div><button onClick={()=>save(scene)} disabled={saving===scene.id} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm text-white"><Save size={16}/>{saving===scene.id?"Saving…":"Save scene"}</button></article>)}</div></div>;
}
