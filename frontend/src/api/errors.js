export function apiErrorMessage(error, fallback = "The request failed. Please try again.") {
    const detail = error?.response?.data?.detail;
    if (typeof detail === "string" && detail) return detail;
    if (Array.isArray(detail)) return detail.map(item => item.msg).filter(Boolean).join(". ") || fallback;
    if (typeof detail?.message === "string") return detail.message;
    if (!error?.response && (error?.code === "ERR_NETWORK" || error?.message === "Network Error")) {
        return "Cannot reach the backend. Check that it is running, then retry. Check Posting records before creating another schedule if a request was interrupted.";
    }
    return error?.response ? fallback : error?.message || fallback;
}
