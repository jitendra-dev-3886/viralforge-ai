import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axios";

export default function UserProviderSelector({ value, onChange, disabled }) {
    const [providers, setProviders] = useState([]);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState("");
    useEffect(() => {
        let active = true;
        api.get("/ai-settings/").then(({ data }) => { if (active) setProviders(data.providers.filter((item) => item.is_active && item.has_key && item.model && (item.provider !== "cloudflare" || item.account_id))); }).catch(() => { if (active) setError("Unable to load API settings. Sign in again if your session expired."); }).finally(() => { if (active) setLoaded(true); });
        return () => { active = false; };
    }, []);
    return <div className="space-y-2">
        <label className="block text-sm font-medium">My AI provider<select disabled={disabled || !loaded} value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 w-full rounded-xl border bg-white p-3">
            <option value="auto">Auto — my enabled providers</option>
            {value !== "auto" && !providers.some((item) => item.provider === value) && <option value={value} disabled>{value} — configure in Settings</option>}
            {providers.map((item) => <option key={item.provider} value={item.provider}>{item.provider} · {item.model}</option>)}
        </select></label>
        {error && <p className="text-xs text-red-700">{error}</p>}
        {loaded && !error && !providers.length && <p className="text-xs text-amber-700">Add your own API key and model before generating content.</p>}
        <Link to="/settings#ai-providers" className="text-xs text-indigo-600 underline">Manage my API keys and models</Link>
    </div>;
}
