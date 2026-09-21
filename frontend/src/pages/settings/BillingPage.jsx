import { useEffect, useState } from "react";
import api from "../../api/axios";

export default function BillingPage() {
    const [data, setData] = useState(null);
    const [plans, setPlans] = useState([]);
    const [history, setHistory] = useState({ exports: [], grants: [] });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const load = async () => {
        setLoading(true); setError("");
        try { const [current, catalog, activity] = await Promise.all([api.get("/billing/me"), api.get("/billing/plans"), api.get("/billing/history")]); setData(current.data); setPlans(catalog.data.plans); setHistory(activity.data); }
        catch (err) { setError(typeof err.response?.data?.detail === "string" ? err.response.data.detail : "Unable to load plans and usage."); }
        finally { setLoading(false); }
    };
    useEffect(() => { load(); }, []);
    const plan = data?.plan;
    const usage = data?.usage;
    const meter = (label, value, limit, suffix = "") => <article key={label} className="rounded-xl border bg-white p-4"><p className="text-sm text-slate-500">{label}</p><strong className="mt-1 block text-xl">{value}{suffix} / {limit}{suffix}</strong><progress className="mt-3 h-2 w-full accent-indigo-600" max={limit || 1} value={Math.min(value, limit || 1)} /></article>;
    return <div className="mx-auto max-w-6xl space-y-6 pb-10">
        <header><h1 className="text-3xl font-bold">Plans & usage</h1><p className="mt-2 text-sm text-slate-500">Choose the allowance that fits your content workflow. AI provider charges are separate and use your own API key.</p></header>
        <p className="rounded-xl bg-amber-50 p-4 text-sm text-amber-900">Payments are not connected yet. Prices below are proposed monthly prices. No payment is collected and no plan renews automatically. Contact the administrator for complimentary pilot access.</p>
        {error && <p role="alert" className="rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}
        <button type="button" disabled={loading} onClick={load} className="rounded-lg border px-4 py-2 text-sm">{loading ? "Loading..." : "Refresh usage"}</button>
        {data && <section className="space-y-4"><div><h2 className="text-xl font-semibold">{plan?.name || "Unrecognized plan"} · {data.status}</h2><p className="mt-1 text-sm text-slate-500">Period ends {data.expires_at ? new Date(data.expires_at).toLocaleString() : "—"}. Existing saved content remains available after expiry.</p></div>
            <div className="grid gap-3 sm:grid-cols-3">{meter("Brands", data.brands_used, plan?.brands || 0)}{plan?.video_exports != null ? meter("Video exports", usage.video_exports, plan.video_exports) : meter("Video minutes", Math.round(usage.video_seconds / 60 * 100) / 100, (plan?.video_seconds || 0) / 60)}{meter("Image exports", usage.image_exports, plan?.image_exports || 0)}</div>
            <p className="text-xs text-slate-500">Usage includes running exports. Each carousel slide counts as one image. Video duration is rounded up to whole seconds per scene, including narration. Completed re-exports count again; failed renders do not. Only one export runs per account at a time.</p>
            {usage.pending > 0 && <p className="rounded-xl bg-indigo-50 p-3 text-sm">An export is pending. Its allowance is reserved until it finishes. If the server stopped during rendering, contact the administrator to release it.</p>}
        </section>}
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{plans.map((item) => <article key={item.code} className={`rounded-2xl border bg-white p-5 ${item.code === plan?.code ? "border-indigo-500" : "border-slate-200"}`}>
            <h2 className="text-lg font-bold">{item.name}</h2><p className="my-3 text-2xl font-bold">{item.price_inr ? `₹${item.price_inr.toLocaleString("en-IN")}` : "Free"}<span className="text-sm font-normal text-slate-500">{item.price_inr ? " / month (proposed)" : " for 7 days"}</span></p>
            <ul className="space-y-2 text-sm text-slate-600"><li>{item.brands} brand{item.brands === 1 ? "" : "s"}</li><li>{item.video_exports != null ? `${item.video_exports} video exports` : `${item.video_seconds / 60} video minutes`}</li><li>{item.image_exports} image exports</li><li>Your own AI API key</li></ul>
            <p className="mt-4 text-xs font-semibold text-indigo-700">{item.code === plan?.code && data?.status === "active" ? "Current plan" : item.code === "trial" ? "One trial per account" : "Pilot grants available through admin"}</p>
        </article>)}</section>
        <section className="rounded-2xl border bg-white p-5"><h2 className="text-lg font-semibold">Access history</h2>{!history.grants.length ? <p className="mt-2 text-sm text-slate-500">No pilot grants recorded. No payments have been collected.</p> : history.grants.map((item, index) => <p key={index} className="mt-2 text-sm">{item.plan} · {item.type} · {new Date(item.starts_at).toLocaleDateString()} – {new Date(item.expires_at).toLocaleDateString()}</p>)}</section>
        <section className="rounded-2xl border bg-white p-5"><h2 className="text-lg font-semibold">Recent exports</h2><div className="mt-3 space-y-2">{history.exports.map((item) => <div key={item.id} className="flex flex-wrap justify-between gap-2 border-b py-2 text-sm"><span>{new Date(item.created_at).toLocaleString()} · {item.kind}</span><span>{item.status === "failed" ? "0 charged" : item.kind === "video" ? `${item.units} seconds` : `${item.units} image`} · {item.status}</span></div>)}{!history.exports.length && <p className="text-sm text-slate-500">No exports recorded yet.</p>}</div></section>
    </div>;
}
