import UserProviderSelector from "../settings/UserProviderSelector";
import { Link } from "react-router-dom";
import VisualStyleSelector from "../ai/VisualStyleSelector";
import TrendingTopics from "../ai/TrendingTopics";
import { assetUrl } from "../../api/axios";
import { FORMATS, isVideoFormat } from "./workflow";

const field = "mt-1 block w-full rounded-xl border border-slate-300 bg-white p-3 text-sm text-slate-900";
export default function BriefStep({ brief, onChange, projects, niches, brand, busy, hasContent, onGenerate }) {
    const update = (name, value) => onChange({ ...brief, [name]: value });
    return <div className="space-y-5">
        <div><h2 className="text-xl font-bold">What are we creating?</h2><p className="mt-1 text-sm text-slate-500">Create one output at a time, then carry it through every step.</p></div>
        {!projects.length && <p className="rounded-xl bg-amber-50 p-4 text-sm">You need a project first. <Link className="font-semibold underline" to="/projects/create">Create a project</Link>, then return here.</p>}
        <fieldset disabled={busy} className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm font-medium">Project<select className={field} value={brief.projectId} onChange={(e) => update("projectId", e.target.value)}><option value="">Select project</option>{projects.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label>
            <label className="text-sm font-medium">Niche<select className={field} value={brief.niche} onChange={(e) => update("niche", e.target.value)}><option value="">Select niche</option>{niches.map((item) => <option key={item.id} value={item.name}>{item.name}</option>)}</select></label>
            <label className="text-sm font-medium">Platform<select className={field} value={brief.platform} onChange={(e) => onChange({ ...brief, platform: e.target.value, format: FORMATS[e.target.value][0] })}>{Object.keys(FORMATS).map((item) => <option key={item}>{item}</option>)}</select></label>
            <label className="text-sm font-medium">Format<select className={field} value={brief.format} onChange={(e) => update("format", e.target.value)}>{FORMATS[brief.platform].map((item) => <option key={item}>{item}</option>)}</select></label>
            <div className="sm:col-span-2">
                <TrendingTopics niche={brief.niche} value={brief.topic} onSelect={(topic) => update("topic", topic)} title="Choose a topic" />
                <label className="mt-3 block text-sm font-medium">Selected topic / brief<textarea rows={3} className={field} value={brief.topic} onChange={(e) => update("topic", e.target.value)} placeholder="Choose a suggestion above or enter your own topic" /></label>
            </div>
            <label className="text-sm font-medium">Language<select className={field} value={brief.language} onChange={(e) => update("language", e.target.value)}>{["English", "Hindi", "Hinglish"].map((item) => <option key={item}>{item}</option>)}</select></label>
            <label className="text-sm font-medium">Writing tone<select className={field} value={brief.tone} onChange={(e) => update("tone", e.target.value)}>{["Educational", "Energetic", "Storytelling", "Promotional", "Inspirational", "Funny"].map((item) => <option key={item}>{item}</option>)}</select></label>
            {!["Quote", "Post", "Community Post"].includes(brief.format) && <label className="text-sm font-medium">Scenes / slides<select className={field} value={brief.scenes} onChange={(e) => update("scenes", Number(e.target.value))}>{[3, 5, 7].map((item) => <option key={item}>{item}</option>)}</select></label>}
            {isVideoFormat(brief.format) && <label className="text-sm font-medium">Target duration<select className={field} value={brief.duration} onChange={(e) => update("duration", Number(e.target.value))}>{[15, 30, 60].map((item) => <option key={item} value={item}>{item} seconds</option>)}</select></label>}
            <UserProviderSelector value={brief.provider} onChange={(provider) => update("provider", provider)} disabled={busy} />
        </fieldset>
        <VisualStyleSelector platform={brief.platform} value={brief.visualStyle} onChange={(value) => update("visualStyle", value)} topic={brief.topic} brandName={brand?.name} logo={assetUrl(brand?.logo)} disabled={busy} />
        {hasContent && <p className="text-sm text-slate-500">Generating creates a new content item. Your current saved item stays in History.</p>}
        <button type="button" disabled={busy || !projects.length} onClick={onGenerate} className="rounded-xl bg-indigo-600 px-6 py-3 font-semibold text-white disabled:opacity-50">{busy ? "Working..." : hasContent ? "Generate new content" : "Generate & review script"}</button>
    </div>;
}
