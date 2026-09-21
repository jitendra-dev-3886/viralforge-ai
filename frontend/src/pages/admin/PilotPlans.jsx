import { useEffect, useState } from "react";
import api from "../../api/axios";

export default function PilotPlans({ users }) {
    const [userId, setUserId] = useState("");
    const [plan, setPlan] = useState("creator");
    const [note, setNote] = useState("");
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState("");
    const [pending, setPending] = useState([]);
    const [confirmed, setConfirmed] = useState({});
    const load = async () => setPending((await api.get("/billing/admin/pending")).data.exports);
    useEffect(() => { load().catch(() => setMessage("Unable to load pending exports.")); }, []);
    const perform = async (operation, success) => { setBusy(true); setMessage(""); try { await operation(); setMessage(success); await load(); } catch (error) { setMessage(typeof error.response?.data?.detail === "string" ? error.response.data.detail : "Unable to complete this action."); } finally { setBusy(false); } };
    return <section className="mt-6 space-y-4 rounded-2xl bg-white p-5 shadow-sm"><h2 className="text-xl font-semibold">Pilot plan access</h2><p className="text-sm text-slate-500">Grant 30 days of complimentary access. This does not record a payment or create recurring billing. Active pilot periods cannot be reset; wait until expiry before granting another period.</p>
        <form onSubmit={(e) => { e.preventDefault(); perform(() => api.post(`/billing/admin/users/${userId}/grant`, { plan, note }), "Complimentary plan granted for 30 days."); }}><fieldset disabled={busy} className="grid gap-3 sm:grid-cols-2"><label className="text-sm">User<select required value={userId} onChange={(e) => setUserId(e.target.value)} className="mt-1 w-full rounded-lg border p-3"><option value="">Select user</option>{users.map((user) => <option key={user.id} value={user.id}>{user.name} · {user.email}</option>)}</select></label><label className="text-sm">Plan<select value={plan} onChange={(e) => setPlan(e.target.value)} className="mt-1 w-full rounded-lg border p-3">{["creator", "pro", "agency"].map((name) => <option key={name}>{name}</option>)}</select></label><label className="text-sm">Reason for grant<input required minLength={5} maxLength={500} value={note} onChange={(e) => setNote(e.target.value)} className="mt-1 w-full rounded-lg border p-3" placeholder="Pilot customer onboarding" /></label><button className="self-end rounded-lg bg-indigo-600 p-3 font-semibold text-white">Grant complimentary access</button></fieldset></form>
        {message && <p role="status" className="text-sm text-slate-700">{message}</p>}
        <div className="flex items-center justify-between"><h3 className="font-semibold">Pending render reservations</h3><button disabled={busy} onClick={() => perform(load, "Pending list refreshed.")} className="rounded-lg border px-3 py-2 text-sm">Refresh</button></div>
        <p className="text-xs text-slate-500">Release only after confirming the render process has stopped, such as after a server restart. Releasing a running job could allow overlapping exports.</p>
        {pending.map((item) => <article key={item.id} className="space-y-2 rounded-lg border p-3 text-sm"><p>User {item.user_id} · {item.resource} · {new Date(item.created_at).toLocaleString()}</p><label className="flex items-center gap-2"><input type="checkbox" checked={Boolean(confirmed[item.id])} onChange={(e) => setConfirmed({ ...confirmed, [item.id]: e.target.checked })} />I confirmed this render worker has stopped.</label><button disabled={busy || !confirmed[item.id]} onClick={() => perform(() => api.post(`/billing/admin/exports/${item.id}/release`, { confirmed_stopped: true }), "Interrupted reservation released; no allowance charged.")} className="rounded-lg border px-3 py-2 disabled:opacity-40">Release interrupted export</button></article>)}
    </section>;
}
