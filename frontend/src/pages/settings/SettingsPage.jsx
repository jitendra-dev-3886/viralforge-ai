import AIProviders from "./AIProviders";
import { useEffect, useState } from "react";
import { createNiche, deleteNiche, getNiches, updateNiche } from "../../api/niche";
import { useNiches } from "../../context/NicheContext";

const emptyForm = { name: "", description: "", icon: "✨", color: "blue", is_active: true };

export default function SettingsPage() {
  const { loadNiches } = useNiches();
  const [niches, setNiches] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const refresh = async () => setNiches((await getNiches(true)).niches || []);
  useEffect(() => { refresh().catch(() => setError("Unable to load niches.")); }, []);

  const save = async (event) => {
    event.preventDefault(); setError("");
    try {
      if (editingId) await updateNiche(editingId, form); else await createNiche(form);
      setForm(emptyForm); setEditingId(null); await refresh(); await loadNiches();
    } catch (err) { setError(err.response?.data?.detail || "Unable to save niche."); }
  };
  const edit = (niche) => { setEditingId(niche.id); setForm({ name: niche.name, description: niche.description || "", icon: niche.icon || "✨", color: niche.color || "blue", is_active: niche.is_active }); };
  const toggle = async (niche) => { await updateNiche(niche.id, { is_active: !niche.is_active }); await refresh(); await loadNiches(); };
  const remove = async (niche) => { if (!window.confirm(`Delete ${niche.name}?`)) return; await deleteNiche(niche.id); await refresh(); await loadNiches(); };

  return <div className="p-1 sm:p-4 lg:p-8">
    <div className="mb-8"><h1 className="text-3xl font-bold">Settings</h1><p className="mt-2 text-slate-500">Manage workspace preferences and niches shown across ViralForge.</p></div>
    <AIProviders />
    {error && <p className="mb-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    <section className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">Niche management</h2><p className="mt-1 text-sm text-slate-500">Enabled niches appear in brand forms and Content Generation.</p>
      <form onSubmit={save} className="mt-5 grid gap-3 md:grid-cols-[90px_1fr_2fr_130px_auto]">
        <input value={form.icon} onChange={(e) => setForm({ ...form, icon: e.target.value })} maxLength={20} className="rounded-xl border p-3" aria-label="Niche icon" />
        <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required minLength={2} placeholder="Niche name" className="rounded-xl border p-3" />
        <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" className="rounded-xl border p-3" />
        <select value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} className="rounded-xl border p-3">{["blue","amber","emerald","indigo","violet","rose"].map(c => <option key={c}>{c}</option>)}</select>
        <button className="rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white">{editingId ? "Update" : "Add niche"}</button>
      </form>
      {editingId && <button onClick={() => { setEditingId(null); setForm(emptyForm); }} className="mt-2 text-sm text-slate-500">Cancel editing</button>}
      <div className="mt-6 space-y-3">{niches.map(niche => <article key={niche.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border p-4">
        <div className="flex items-center gap-3"><span className="text-2xl">{niche.icon}</span><div><strong>{niche.name}</strong><p className="text-sm text-slate-500">{niche.description}</p></div></div>
        <div className="flex gap-2"><button onClick={() => toggle(niche)} className={`rounded-lg px-3 py-2 text-sm ${niche.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>{niche.is_active ? "Visible" : "Hidden"}</button><button onClick={() => edit(niche)} className="rounded-lg border px-3 py-2 text-sm">Edit</button><button onClick={() => remove(niche)} className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">Delete</button></div>
      </article>)}</div>
    </section>
  </div>;
}
