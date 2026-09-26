import { CONTENT_GOALS } from "./contentGoals";

export default function ContentGoalSelector({ value, onChange, disabled = false }) {
    return <label className="block text-sm font-medium">Content Goal
        <select value={value || ""} onChange={(event) => onChange(event.target.value)} disabled={disabled}
            className="mt-1 block w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900">
            <option value="">Default engagement</option>
            {CONTENT_GOALS.map((goal) => <option key={goal} value={goal}>{goal}</option>)}
        </select>
        {value === "Shares" && <span className="mt-1 block text-xs font-normal text-slate-500">AI chooses a natural reason for your audience to share.</span>}
    </label>;
}
