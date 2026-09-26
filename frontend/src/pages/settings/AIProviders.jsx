import { useEffect, useState } from "react";
import api from "../../api/axios";
const providers = [
  "gemini",
  "groq",
  "cerebras",
  "openrouter",
  "mistral",
  "cloudflare",
  "huggingface",
];
const links = {
  gemini: "https://aistudio.google.com/apikey",
  groq: "https://console.groq.com/keys",
  cerebras: "https://cloud.cerebras.ai/",
  openrouter: "https://openrouter.ai/settings/keys",
  mistral: "https://console.mistral.ai/api-keys",
  cloudflare: "https://dash.cloudflare.com/profile/api-tokens",
  huggingface: "https://huggingface.co/settings/tokens",
};
export default function AIProviders() {
  const [items, setItems] = useState([]);
  const [provider, setProvider] = useState("gemini");
  const [model, setModel] = useState("");
  const [accountId, setAccountId] = useState("");
  const [key, setKey] = useState("");
  const [active, setActive] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const refresh = async () => {
    const result = await api.get("/ai-settings/");
    setItems(result.data.providers);
  };
  useEffect(() => {
    let mounted = true;
    api
      .get("/ai-settings/")
      .then(({ data }) => {
        if (mounted) {
          setItems(data.providers);
          const initial = data.providers.find(
            (item) => item.provider === "gemini",
          );
          setModel(initial?.model || "");
          setActive(initial?.is_active ?? true);
        }
      })
      .catch(() => {
        if (mounted)
          setMessage(
            "Unable to load your API settings. Sign in again if your session expired.",
          );
      });
    return () => {
      mounted = false;
    };
  }, []);
  const select = (value) => {
    const saved = items.find((item) => item.provider === value);
    setProvider(value);
    setAccountId(saved?.account_id || "");
    setModel(saved?.model || "");
    setActive(saved?.is_active ?? true);
    setKey("");
    setMessage("");
  };
  const saved = items.find((item) => item.provider === provider);
  const save = async (event) => {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await api.put(`/ai-settings/${provider}`, {
        model: model.trim(),
        ...(provider === "cloudflare" ? { account_id: accountId.trim() } : {}),
        ...(key.trim() ? { api_key: key.trim() } : {}),
        is_active: active,
      });
      setKey("");
      await refresh();
      setMessage(
        "Saved securely. Generation will use your key and selected model. Saving does not verify provider access.",
      );
    } catch (error) {
      const detail = error.response?.data?.detail;
      setMessage(
        typeof detail === "string"
          ? detail
          : detail?.message ||
              "Unable to save. Check the model ID and API key.",
      );
    } finally {
      setBusy(false);
    }
  };
  const remove = async () => {
    setBusy(true);
    try {
      await api.delete(`/ai-settings/${provider}`);
      setKey("");
      setModel("");
      await refresh();
      setMessage("Provider removed from your account.");
    } catch {
      setMessage("Unable to remove provider.");
    } finally {
      setBusy(false);
    }
  };
  const testProvider = async () => {
    setBusy(true);
    setMessage("Testing saved key and model...");
    try {
      const { data } = await api.post(`/ai-settings/${provider}/test`);
      setMessage(data.message);
    } catch (error) {
      const detail = error.response?.data?.detail;
      setMessage(
        typeof detail === "string"
          ? detail
          : detail?.message ||
              "Test could not complete. Check the backend connection and try again.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <section
      id="ai-providers"
      className="mb-6 space-y-4 rounded-3xl bg-white p-6 shadow-sm"
    >
      <h2 className="text-xl font-semibold">My AI providers</h2>
      <p className="text-sm text-slate-500">
        Add your own provider API key and exact model ID before generating
        content. Auto uses only your enabled providers. Usage is billed by your
        provider; other users cannot use your keys.
      </p>
      <div className="flex flex-wrap gap-2">
        {providers.map((item) => (
          <button
            disabled={busy}
            type="button"
            key={item}
            onClick={() => select(item)}
            className={`rounded-lg border px-3 py-2 text-sm ${provider === item ? "bg-indigo-600 text-white" : "bg-white"}`}
          >
            {item}{" "}
            {items.some((row) => row.provider === item && row.has_key)
              ? "• Saved"
              : ""}
          </button>
        ))}
      </div>
      {["mistral", "cloudflare", "huggingface"].includes(provider) && (
        <p className="text-sm text-slate-500">
          {provider === "cloudflare"
            ? "Use a Workers AI API token, your Account ID, and a text-generation model ID beginning with @cf/."
            : provider === "huggingface"
              ? "Use a Hugging Face token with Inference Providers permission and a chat model available through Inference Providers."
              : "Use your Mistral API key and a chat model available to your account."}{" "}
          Choose a model supporting JSON output. Free access depends on your
          provider's current allowance; this app does not enforce a free-only
          plan.
        </p>
      )}
      <form onSubmit={save}>
        <fieldset disabled={busy} className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            Model ID
            <input
              required
              value={model}
              onChange={(e) => setModel(e.target.value)}
              maxLength={160}
              placeholder="Exact model ID from your provider"
              className="mt-1 w-full rounded-xl border p-3"
            />
          </label>
          {provider === "cloudflare" && (
            <label className="text-sm">
              Cloudflare Account ID
              <input
                required
                pattern="[a-fA-F0-9]{32}"
                maxLength={32}
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                placeholder="32-character Account ID from your dashboard"
                className="mt-1 w-full rounded-xl border p-3"
              />
            </label>
          )}
          <label className="text-sm">
            API key
            <input
              type="password"
              autoComplete="new-password"
              required={!saved?.has_key}
              value={key}
              onChange={(e) => setKey(e.target.value)}
              maxLength={512}
              placeholder={
                saved?.has_key
                  ? "Saved — leave empty to keep it"
                  : "Paste your provider API key"
              }
              className="mt-1 w-full rounded-xl border p-3"
            />
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={active}
              onChange={(e) => setActive(e.target.checked)}
            />
            Enable for my generation requests
          </label>
          <a
            className="text-sm text-indigo-600 underline"
            href={links[provider]}
            target="_blank"
            rel="noreferrer"
          >
            Open {provider} API settings
          </a>
          <button className="rounded-xl bg-indigo-600 p-3 font-semibold text-white">
            {busy ? "Saving..." : "Save provider"}
          </button>
          {saved && (
            <button
              type="button"
              onClick={remove}
              className="rounded-xl border p-3 text-red-700"
            >
              Remove saved provider
            </button>
          )}
          {saved && (
            <button
              type="button"
              disabled={
                Boolean(key.trim()) ||
                model.trim() !== saved.model ||
                active !== saved.is_active ||
                !saved.is_active ||
                (provider === "cloudflare" &&
                  accountId.trim() !== saved.account_id)
              }
              onClick={testProvider}
              className="rounded-xl border p-3 text-indigo-700 disabled:opacity-40"
            >
              Test saved provider
            </button>
          )}
        </fieldset>
      </form>
      <p className="text-xs text-slate-500">
        Save changes before testing. The test sends a small JSON request using
        this provider's saved key and model and may use provider credits. Each
        provider needs its own API key.
      </p>
      {message && (
        <p role="status" className="text-sm text-slate-700">
          {message}
        </p>
      )}
    </section>
  );
}
