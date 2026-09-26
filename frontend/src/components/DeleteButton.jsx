import { useRef, useState } from "react";
import { LoaderCircle, Trash2 } from "lucide-react";

export default function DeleteButton({ label, description, onDelete, onDeleted, disabled = false, buttonLabel = "Delete" }) {
    const [pending, setPending] = useState(false);
    const [error, setError] = useState("");
    const inFlight = useRef(false);

    const handleDelete = async () => {
        if (disabled || inFlight.current || !window.confirm(`Delete ${label}?\n\n${description || "This item will be removed from your library."}\nThis cannot be undone.`)) return;
        inFlight.current = true;
        setPending(true);
        setError("");
        try {
            const result = await onDelete();
            if (result?.success !== true) throw new Error(result?.message || "Deletion failed. Please try again.");
        } catch (err) {
            const detail = err.response?.data?.detail;
            setError(typeof detail === "string" ? detail : err.response?.data?.message || err.message || "Unable to delete this item.");
            return;
        } finally {
            inFlight.current = false;
            setPending(false);
        }
        onDeleted();
    };

    return <div className="shrink-0">
        <button type="button" onClick={handleDelete} disabled={pending || disabled} aria-label={`Delete ${label}`} className="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100 focus-visible:outline-2 focus-visible:outline-red-600 disabled:cursor-wait disabled:opacity-60">
            {pending ? <LoaderCircle size={15} className="animate-spin" /> : <Trash2 size={15} />}
            {pending ? "Deleting..." : buttonLabel}
        </button>
        {error && <p role="alert" className="mt-2 max-w-xs text-sm text-red-700">{error}</p>}
    </div>;
}
