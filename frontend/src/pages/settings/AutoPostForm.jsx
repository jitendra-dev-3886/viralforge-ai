import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getSocialConnections } from "../../api/social";
import { getProjectMedia } from "../../api/media";
import { getContentScenes } from "../../api/scene";
import { createSchedule } from "../../api/schedule";
import { assetUrl } from "../../api/axios";
import { apiErrorMessage } from "../../api/errors";

export default function AutoPostForm({ content, disabled, onScheduled }) {
    const [accounts, setAccounts] = useState([]);
    const [assets, setAssets] = useState([]);
    const [accountId, setAccountId] = useState("");
    const [mediaIds, setMediaIds] = useState([]);
    const [when, setWhen] = useState("");
    const [privacy, setPrivacy] = useState("public");
    const [kids, setKids] = useState("");
    const [busy, setBusy] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [enabled, setEnabled] = useState(false);
    const requestRef = useRef(null);
    const lock = useRef(false);
    const platform = content.platform.toLowerCase();
    const privateDraft = platform === "youtube" && privacy === "private";
    useEffect(() => {
        let active = true;
        setAssets([]);
        setMediaIds([]);
        setLoaded(false);
        setError("");
        setNotice("");
        requestRef.current = null;
        Promise.all([getSocialConnections(), getProjectMedia(content.project_id), getContentScenes(content.id)]).then(([connections, media, scenes]) => {
            if (!active) return;
            setAccounts(connections.accounts.filter(item => item.status === "connected" && item.provider === platform));
            setEnabled(connections.worker_enabled);
            const exportName = new RegExp(`^content_${Number(content.id)}_(?:final\\.mp4|scene_\\d+_final\\.(?:png|jpe?g|webp|mp4))$`, "i");
            const sceneMediaIds = new Set((scenes.scenes || []).map(scene => scene.media_id));
            setAssets((media.media || []).filter(item => item.status === "ready"
                && ["image", "video", "render", "final"].includes(item.media_type)
                && (sceneMediaIds.has(item.id) || exportName.test(item.file_name))
                && (platform !== "youtube" || ["video", "render", "final"].includes(item.media_type))));
            setLoaded(true);
        }).catch(err => { if (active) setError(apiErrorMessage(err, "Unable to load publishing accounts or media.")); });
        return () => { active = false; };
    }, [content.id, content.project_id, platform]);
    const toggleMedia = id => setMediaIds(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id]);
    const submit = async () => {
        if (lock.current) return;
        setError("");
        setNotice("");
        const date = new Date(when);
        if (!accountId || !mediaIds.length || !Number.isFinite(date.getTime()) || date <= new Date()) { setError("Choose a connected account, media and a future date/time."); return; }
        if (platform === "youtube" && !kids) { setError("Choose the YouTube audience setting."); return; }
        const payload = { project_id: content.project_id, content_id: content.id, platform: content.platform, publishing_account_id: Number(accountId), media_ids: mediaIds, scheduled_at: date.toISOString(), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, privacy, made_for_kids: kids === "yes" };
        const signature = JSON.stringify(payload);
        if (requestRef.current?.signature !== signature) requestRef.current = { signature, key: crypto.randomUUID() };
        lock.current = true; setBusy(true);
        try {
            const result = await createSchedule({ ...payload, request_key: requestRef.current.key });
            setWhen(""); setMediaIds([]); requestRef.current = null;
            setNotice(privateDraft ? "Private YouTube upload scheduled. Review it in YouTube Studio after upload." : "Automatic post scheduled. You can check its status in Posting records.");
            try { await onScheduled(result.schedule); }
            catch { setNotice("Your post was scheduled, but the list could not refresh. Open Scheduler to check its status."); }
        } catch (err) { setError(apiErrorMessage(err, "Unable to schedule. Retry with the same selection to avoid creating a duplicate job.")); }
        finally { lock.current = false; setBusy(false); }
    };
    const selected = mediaIds.map(id => assets.find(asset => asset.id === id)).filter(Boolean);
    return <fieldset disabled={disabled || busy} className="space-y-4 rounded-2xl border border-indigo-100 bg-white p-5">
        <div><h3 className="font-semibold">Automatic posting</h3><p className="mt-1 text-sm text-slate-500">Select the account and the exact files to publish. The caption and media selection are saved with this schedule.</p></div>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        {notice && <p role="status" className="text-sm text-emerald-700">{notice}</p>}
        {!loaded && !error && <p role="status" className="text-sm text-slate-500">Loading publishing options...</p>}
        {loaded && !enabled && <p className="text-sm text-amber-700">Automatic publishing is disabled on this server.</p>}
        {loaded && !accounts.length && <p className="text-sm text-amber-700">Connect a {content.platform} account in <Link to="/settings#social-accounts" className="underline">Settings → Connected social accounts</Link>.</p>}
        <label className="block text-sm font-medium">Publish to<select required value={accountId} onChange={event => setAccountId(event.target.value)} className="mt-2 block w-full rounded-xl border p-3"><option value="">Select connected account</option>{accounts.map(account => <option key={account.id} value={account.id}>{account.name}</option>)}</select></label>
        <div><p className="text-sm font-medium">Media to publish</p><p className="mt-1 text-xs text-slate-500">Showing scene media and finished exports for this content only. Use the final export for the complete video with captions and branding. {platform === "youtube" ? "YouTube requires a video." : "Choose one video or up to 10 images in posting order."}</p>
            <div className="mt-2 max-h-56 space-y-2 overflow-y-auto rounded-xl border p-3">{assets.map(asset => <label key={asset.id} className="flex items-center gap-3 text-sm"><input type="checkbox" checked={mediaIds.includes(asset.id)} disabled={!mediaIds.includes(asset.id) && mediaIds.length >= 10} onChange={() => toggleMedia(asset.id)} /><span>{asset.title || asset.file_name} <span className="text-xs text-slate-500">({asset.media_type})</span></span>{mediaIds.includes(asset.id) && <span className="text-xs text-indigo-600">#{mediaIds.indexOf(asset.id) + 1}</span>}</label>)}{loaded && !assets.length && <p className="text-sm text-slate-500">Export your content first, then reopen scheduling.</p>}</div>
        </div>
        {selected.length > 0 && <div className="flex flex-wrap gap-3">{selected.map(asset => <div key={asset.id} className="w-32">{asset.media_type === "image" ? <img alt={asset.title || "Selected image"} src={assetUrl(asset.file_url)} className="h-32 w-32 rounded-xl object-contain" /> : <video controls preload="metadata" src={assetUrl(asset.file_url)} className="h-32 w-32 rounded-xl object-contain" />}<p className="mt-1 truncate text-xs">{asset.title || asset.file_name}</p></div>)}</div>}
        <p className="whitespace-pre-wrap rounded-xl bg-slate-50 p-3 text-sm">{content.caption || "No caption"}{content.hashtags?.length ? `\n\n${Array.isArray(content.hashtags) ? content.hashtags.join(" ") : content.hashtags.replaceAll(",", " ")}` : ""}</p>
        {platform === "facebook" && <p className="text-xs text-slate-500">Videos publish as Facebook Page Reels. Images publish as a Page photo post.</p>}
        {platform === "instagram" && <p className="text-xs text-slate-500">Images publish to the feed; videos publish as Reels. Feed images need a 4:5 to 1.91:1 aspect ratio.</p>}
        {platform === "youtube" && <div className="grid gap-3 sm:grid-cols-2"><label className="text-sm">YouTube posting mode<select value={privacy} onChange={event => setPrivacy(event.target.value)} className="mt-2 block w-full rounded-xl border p-3"><option value="public">Public</option><option value="unlisted">Unlisted</option><option value="private">Draft ? upload as Private</option></select></label><label className="text-sm">Made for kids?<select value={kids} onChange={event => setKids(event.target.value)} className="mt-2 block w-full rounded-xl border p-3"><option value="">Choose audience</option><option value="no">No, not made for kids</option><option value="yes">Yes, made for kids</option></select></label></div>}
        {privateDraft && <p role="status" className="rounded-xl bg-indigo-50 p-3 text-sm text-indigo-800">This uploads a private video to YouTube at the chosen time. It stays private until you change its visibility in YouTube Studio. Your title, description, hashtags and keyword tags are included.</p>}
        <label className="block text-sm">{privateDraft ? "Private upload date and time" : "Publish date and time"} ({Intl.DateTimeFormat().resolvedOptions().timeZone})<input type="datetime-local" required value={when} onChange={event => setWhen(event.target.value)} className="mt-2 block rounded-xl border p-3" /></label>
        <button type="button" disabled={!loaded || !enabled || !accountId || !mediaIds.length || !when || content.status !== "approved" || (platform === "youtube" && !kids)} onClick={submit} className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-40">{busy ? "Saving schedule..." : privateDraft ? "Schedule private draft upload" : "Schedule automatic post"}</button>
        <p className="text-xs text-slate-500">Your server must stay running. Publication may take a few minutes while the platform processes the media.</p>
    </fieldset>;
}
