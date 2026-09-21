import requests
import re
from urllib.parse import quote

ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "cerebras": "https://api.cerebras.ai/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "mistral": "https://api.mistral.ai/v1/chat/completions",
    "huggingface": "https://router.huggingface.co/v1/chat/completions",
}


class ProviderAuth(requests.auth.AuthBase):
    """Explicit auth prevents Requests from replacing headers with local netrc auth."""
    def __init__(self, key, google=False):
        self.key, self.google = key, google

    def __call__(self, request):
        request.headers["x-goog-api-key" if self.google else "Authorization"] = self.key if self.google else f"Bearer {self.key}"
        return request


def generate_user_content(provider, prompt, credentials, *, max_tokens=None):
    """Request-local credentials only. Never mutate globals or use server keys."""
    key, model = credentials["api_key"], credentials["model"]
    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model.removeprefix('models/'), safe='')}:generateContent"
        headers = {"x-goog-api-key": key}
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 8192}}
    else:
        if provider == "cloudflare":
            account = credentials.get("account_id", "")
            if not re.fullmatch(r"[a-fA-F0-9]{32}", account):
                raise ValueError("A valid Cloudflare Account ID is required")
            url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1/chat/completions"
        else:
            url = ENDPOINTS[provider]
        headers = {"Authorization": f"Bearer {key}"}
        body = {"model": model, "messages": [{"role": "system", "content": "Return one complete JSON object only."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "max_tokens": 4096, "stream": False}
    if max_tokens is not None:
        if provider == "gemini":
            body["generationConfig"]["maxOutputTokens"] = max_tokens
        else:
            body["max_tokens"] = max_tokens
    response = requests.post(url, headers=headers, auth=ProviderAuth(key, provider == "gemini"), json=body, timeout=(10, 180), allow_redirects=False)
    if not 200 <= response.status_code < 300:
        # Deliberately omit provider response bodies and request headers from errors.
        error = RuntimeError(f"Provider HTTP {response.status_code}")
        error.status_code = response.status_code
        # Classify known provider reasons without exposing their raw response.
        try:
            detail = response.json().get("error", {})
            message = str(detail.get("message", "")).lower() if isinstance(detail, dict) else ""
            code = detail.get("code") if isinstance(detail, dict) else None
            if provider == "groq" and response.status_code == 403 and (code == "model_permission_blocked_project" or "blocked at the project level" in message):
                error.access_reason = "project_model_blocked"
            if provider == "gemini" and response.status_code == 404 and "no longer available to new users" in message:
                error.access_reason = "model_unavailable_new_users"
        except (ValueError, AttributeError, TypeError):
            pass
        if provider == "openrouter" and response.status_code == 401:
            try:
                check = requests.get("https://openrouter.ai/api/v1/key", auth=ProviderAuth(key), timeout=(10, 15), allow_redirects=False)
                info = check.json().get("data", {}) if check.status_code == 200 else {}
                if info.get("is_management_key") or info.get("is_provisioning_key"):
                    error.credential_role = "management"
            except (requests.RequestException, ValueError, AttributeError, TypeError):
                pass  # Preserve the original generation failure if diagnostics fail.
        raise error
    data = response.json()
    if provider == "gemini":
        candidates = data.get("candidates") or []
        if not candidates or candidates[0].get("finishReason") == "MAX_TOKENS":
            raise ValueError("Provider returned empty or truncated content")
        text = "".join(part.get("text", "") for part in candidates[0].get("content", {}).get("parts", []) if not part.get("thought"))
    else:
        choices = data.get("choices") or []
        if not choices or choices[0].get("finish_reason") == "length":
            raise ValueError("Provider returned empty or truncated content")
        text = choices[0].get("message", {}).get("content")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Provider returned no text")
    return text, model
