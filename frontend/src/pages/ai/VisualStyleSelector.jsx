import { useState } from "react";
import { VISUAL_STYLES as presets, getVisualStyle } from "./visualStyles";

import { SampleComposition } from "./StyleArtwork";

const formats = [
    { id: "reel", label: "Reel / Story", ratio: "9 / 16" },
    { id: "carousel", label: "Carousel", ratio: "4 / 5" },
    { id: "post", label: "Post / Quote", ratio: "1 / 1" },
    { id: "video", label: "Long video", ratio: "16 / 9" },
];

export default function VisualStyleSelector({ value, onChange, topic, brandName, logo, platform, disabled }) {
    const [format, setFormat] = useState("post");
    const preset = getVisualStyle(value) || presets[0];
    const selectedFormat = formats.find((item) => item.id === format);
    return <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6" aria-labelledby="visual-style-title">
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">Choose your look</p>
        <h2 id="visual-style-title" className="mt-2 text-xl font-bold text-slate-900">Visual style</h2>
        <p className="mt-2 text-sm text-slate-500">Full photo or video with compact translucent captions. TV Series and Documentary use your brand name; other designs use their own logo and username treatment.</p>
        <div className="mt-6 grid gap-7 lg:grid-cols-[1fr_340px]">
            <fieldset disabled={disabled} className="grid grid-cols-2 gap-3 self-start">
                <legend className="sr-only">Select a visual style</legend>
                {presets.map((item) => <label key={item.id} className={`relative cursor-pointer rounded-2xl border-2 p-3 transition focus-within:ring-4 focus-within:ring-indigo-200 ${value === item.id ? "border-indigo-600 bg-indigo-50" : "border-slate-100 hover:border-slate-300"} ${disabled ? "cursor-wait opacity-60" : ""}`}>
                    <input type="radio" name="visual-style" value={item.id} checked={value === item.id} onChange={() => onChange(item.id)} className="sr-only" />
                    <div data-style-stage className="relative mb-3 w-full overflow-hidden rounded-lg" style={{ aspectRatio: "4 / 5", containerType: "size", background: item.background }} aria-hidden="true">
                        <SampleComposition preset={item} compact brandName={brandName} logo={logo} platform={platform} />
                    </div>
                    <span className="block text-sm font-bold text-slate-900">{item.name}{value === item.id && <span className="ml-2 text-indigo-600" aria-hidden="true">✓</span>}</span>
                    {item.brandingLabel && <span className="mt-1 block text-xs font-semibold text-indigo-700">{item.brandingLabel} branding</span>}
                    <span className="mt-1 block text-xs leading-relaxed text-slate-500">{item.description}</span>
                </label>)}
            </fieldset>
            <div className="rounded-2xl bg-slate-100 p-4">
                <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label="Preview format">
                    {formats.map((item) => <button type="button" key={item.id} aria-pressed={format === item.id} onClick={() => setFormat(item.id)} className={`rounded-full px-3 py-1.5 text-xs font-semibold ${format === item.id ? "bg-slate-900 text-white" : "bg-white text-slate-600"}`}>{item.label}</button>)}
                </div>
                <div data-style-stage className="relative mx-auto w-full overflow-hidden rounded-xl shadow-lg" style={{ aspectRatio: selectedFormat.ratio, containerType: "size", background: preset.background }}>
                    <SampleComposition preset={preset} topic={topic} brandName={brandName} logo={logo} platform={platform} />
                </div>
                <p className="mt-3 text-sm font-semibold text-slate-800" aria-live="polite">{preset.name} · {selectedFormat.label}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-500">Sample layout with placeholder artwork. Generated media and text will vary. Video preview shows a still frame.</p>
            </div>
        </div>
    </section>;
}
