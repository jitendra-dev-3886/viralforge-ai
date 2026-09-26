import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getSocialConnections, connectSocial, disconnectSocial } from "../../api/social";

const labels = { instagram: "Instagram", facebook: "Facebook Pages", youtube: "YouTube" };

export default function SocialConnections() {
    const [data, setData] = useState({ accounts: [], providers: [] });
    const [busy, setBusy] = useState("");
    const [error, setError] = useState("");
    const [platform, setPlatform] = useState("instagram");
    const [params] = useSearchParams();
    const refresh = useCallback(async () => setData(await getSocialConnections()), []);
    useEffect(() => { refresh().catch(() => setError("Unable to load social connections.")); }, [refresh]);
    const action = async (key, task) => {
        setBusy(key); setError("");
        try { await task(); } catch (err) { setError(err.response?.data?.detail || "Connection failed. Please try again."); }
        finally { setBusy(""); }
    };
    return <section id="social-accounts" className="mb-6 space-y-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div><h2 className="text-xl font-semibold">Connected social accounts</h2><p className="mt-1 text-sm text-slate-500">Connect Instagram, Facebook Pages and YouTube to publish approved content automatically at a scheduled time.</p></div>
        {params.get("social") === "connected" && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">Account connected. Select it when scheduling a post.</p>}
        {["failed", "cancelled"].includes(params.get("social")) && <p role="alert" className="rounded-xl bg-amber-50 p-3 text-sm text-amber-800">{params.get("social") === "cancelled" ? "Connection was cancelled." : "Connection did not complete. Confirm the app is configured, grant publishing permissions, and use an eligible account, then try again."}</p>}
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <div aria-label="Social platforms" className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
            {Object.entries(labels).map(([value, label]) => <button key={value} type="button" aria-pressed={platform === value} onClick={() => { setPlatform(value); setError(""); }} className={`rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${platform === value ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>{label}</button>)}
        </div>
        <div className="grid gap-3">{data.providers.filter(item => item.provider === platform).map(item => <div key={item.provider} className="rounded-2xl border p-4">
            <h3 className="font-semibold">{labels[item.provider]}</h3>
            <p className="mt-2 text-xs text-slate-500">{item.provider === "instagram" ? "Business or Creator accounts. Images, carousels and Reels." : item.provider === "facebook" ? "Managed Pages. Photo posts and Reels." : "Personal and Brand channels. Connect each channel separately, then choose it in Scheduler."}</p>
            <button type="button" disabled={Boolean(busy) || !item.configured} onClick={() => action(item.provider, async () => { const result = await connectSocial(item.provider); window.location.assign(result.authorization_url); })} className="mt-4 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">{busy === item.provider ? "Connecting..." : item.provider === "youtube" && data.accounts.some(account => account.provider === "youtube" && account.status === "connected") ? "Add another YouTube channel" : `Connect ${labels[item.provider]}`}</button>
            {!item.configured && <p className="mt-2 text-xs text-amber-700">Administrator setup required before connecting.</p>}
        </div>)}</div>
        {data.accounts.filter(account => account.provider === platform).map(account => <article key={account.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-50 p-4">
            <div><strong>{account.name}</strong><p className="text-sm capitalize text-slate-500">{labels[account.provider]} · {account.status.replaceAll("_", " ")}</p>{account.expires_at && <p className="text-xs text-slate-500">Permission expiry: {new Date(account.expires_at).toLocaleString()}</p>}</div>
            {account.status !== "disconnected" && <button type="button" disabled={Boolean(busy)} onClick={() => { if (window.confirm(`Disconnect ${account.name}? Pending automatic posts for this account will be cancelled.`)) action(String(account.id), async () => { await disconnectSocial(account.id); await refresh(); }); }} className="rounded-lg border px-3 py-2 text-sm disabled:opacity-50">Disconnect</button>}
        </article>)}
        <Link to="/scheduler" className="inline-block text-sm font-semibold text-indigo-600 underline">Open Scheduler and posting history</Link>
    </section>;
}
