import { useNiches } from "../../context/NicheContext";

const colors = { amber: "border-amber-500 bg-amber-50", emerald: "border-emerald-500 bg-emerald-50", indigo: "border-indigo-500 bg-indigo-50", violet: "border-violet-500 bg-violet-50", rose: "border-rose-500 bg-rose-50", blue: "border-blue-500 bg-blue-50" };

export default function NicheSelector({ selected, onChange }) {
    const { niches, loading } = useNiches();
    const selectedNiche = niches.find((niche) => niche.name === selected);
    return (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-5 flex items-start justify-between gap-4">
                <div><div className="flex items-center gap-2"><span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">3</span><h2 className="text-lg font-semibold text-slate-900">Choose a niche</h2></div><p className="ml-9 mt-1 text-sm text-slate-500">Only niches enabled in Settings are shown here.</p></div>
                {selectedNiche && <div className="hidden rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 sm:block">{selectedNiche.name}</div>}
            </div>
            {loading ? <p className="text-sm text-slate-500">Loading niches…</p> : <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">{niches.map((niche) => {
                const active = selected === niche.name;
                return <button type="button" key={niche.id} onClick={() => onChange(niche.name)} aria-pressed={active} className={`relative rounded-2xl border p-4 text-center transition hover:-translate-y-0.5 hover:shadow-md ${active ? `${colors[niche.color] || colors.blue} ring-2 ring-blue-100` : "border-slate-200"}`}>
                    {active && <span className="absolute right-2 top-2 rounded-full bg-blue-600 px-1.5 text-xs text-white">✓</span>}<div className="text-3xl">{niche.icon || "✨"}</div><h3 className="mt-3 text-sm font-semibold text-slate-800">{niche.name}</h3><p className="mt-1 text-[11px] leading-4 text-slate-500">{niche.description}</p>
                </button>;
            })}</div>}
            {!loading && niches.length === 0 && <p className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">No visible niches. Add or enable one in Settings.</p>}
        </section>
    );
}
