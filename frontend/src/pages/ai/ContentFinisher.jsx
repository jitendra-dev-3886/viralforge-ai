import { useMemo, useRef, useState } from "react";
import { Download, Grip, Music, Play, RotateCcw, Save } from "lucide-react";
import { updateContent } from "../../api/content";
import { generateProjectRender, uploadProjectMusic } from "../../api/projectRender";
import { assetUrl } from "../../api/axios";

const DEFAULT_LAYOUT = {
    text: { x: 50, y: 68 },
    logo: { x: 10, y: 8 },
    username: { x: 82, y: 92 },
};

const clamp = (value) => Math.max(3, Math.min(97, value));

export default function ContentFinisher({ content, username = "", logo = "", projectId }) {
    const stageRef = useRef(null);
    const [layout, setLayout] = useState(() => ({
        ...DEFAULT_LAYOUT,
        ...(content.generation_config?.overlay_layout || {}),
    }));
    const [dragging, setDragging] = useState(null);
    const [music, setMusic] = useState(null);
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState("");
    const [renderUrl, setRenderUrl] = useState("");

    const scene = content.scenes?.[0];
    const mediaUrl = assetUrl(scene?.media_url);
    const resolvedLogo = assetUrl(logo || content.branding?.logo || content.generation_config?.branding?.logo);
    const resolvedUsername = username || content.branding?.username || content.branding?.brand_name || content.generation_config?.branding?.username || "";
    const contentId = content.id || content.content_id;
    const resolvedProjectId = projectId || content.project_id;
    const aspectRatio = useMemo(() => {
        const type = String(content.content_type || "").toLowerCase();
        const platform = String(content.platform || "").toLowerCase();
        if (/reel|short|story/.test(type)) return "9 / 16";
        if (type.includes("carousel") && platform.includes("instagram")) return "4 / 5";
        if (platform.includes("youtube") && type.includes("video")) return "16 / 9";
        return "1 / 1";
    }, [content.content_type, content.platform]);

    const move = (event) => {
        if (!dragging || !stageRef.current) return;
        const rect = stageRef.current.getBoundingClientRect();
        setLayout((current) => ({
            ...current,
            [dragging]: {
                x: clamp(((event.clientX - rect.left) / rect.width) * 100),
                y: clamp(((event.clientY - rect.top) / rect.height) * 100),
            },
        }));
    };

    const saveLayout = async () => {
        if (!contentId) throw new Error("Content must be saved before editing its layout.");
        await updateContent(contentId, {
            generation_config: {
                ...(content.generation_config || {}),
                branding: {
                    ...(content.generation_config?.branding || content.branding || {}),
                    username: resolvedUsername,
                    logo: logo || content.branding?.logo || content.generation_config?.branding?.logo || "",
                },
                overlay_layout: layout,
            },
        });
    };

    const handleSave = async () => {
        setBusy(true);
        setMessage("");
        try {
            await saveLayout();
            setMessage("Overlay layout saved.");
        } catch (error) {
            setMessage(error.response?.data?.detail || error.message || "Unable to save layout.");
        } finally {
            setBusy(false);
        }
    };

    const handleRender = async () => {
        if (!resolvedProjectId || !contentId) {
            setMessage("Select a saved project and generate content before merging.");
            return;
        }
        if (music && music.size > 25 * 1024 * 1024) {
            setMessage("Background music must be 25 MB or smaller.");
            return;
        }
        setBusy(true);
        setMessage("Saving layout and rendering all scenes…");
        try {
            await saveLayout();
            if (music) await uploadProjectMusic(resolvedProjectId, music);
            const result = await generateProjectRender(resolvedProjectId, contentId);
            const url = result.file_url || result.output_url || result.render?.file_url;
            setRenderUrl(assetUrl(url));
            setMessage("Final post-ready video created with overlays, transitions, narration, and music.");
        } catch (error) {
            setMessage(error.response?.data?.detail || error.message || "Unable to create the final render.");
        } finally {
            setBusy(false);
        }
    };

    if (!scene?.media_url) return null;

    const overlay = (name, children, className = "") => (
        <button
            type="button"
            onPointerDown={(event) => {
                event.currentTarget.setPointerCapture(event.pointerId);
                setDragging(name);
            }}
            onPointerUp={() => setDragging(null)}
            className={`absolute z-10 cursor-grab touch-none select-none active:cursor-grabbing ${className}`}
            style={{ left: `${layout[name]?.x ?? DEFAULT_LAYOUT[name].x}%`, top: `${layout[name]?.y ?? DEFAULT_LAYOUT[name].y}%`, transform: "translate(-50%, -50%)" }}
            aria-label={`Drag ${name} overlay`}
        >
            {children}
        </button>
    );

    return (
        <section className="mt-8 rounded-2xl border border-indigo-200 bg-indigo-50/60 p-4 sm:p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h3 className="text-lg font-bold text-slate-900">Finish & merge</h3>
                    <p className="text-sm text-slate-600">Drag the text, logo, and username. Saved positions are embedded in the final MP4.</p>
                </div>
                <Grip className="text-indigo-500" size={22} />
            </div>

            <div className="grid gap-6 lg:grid-cols-[minmax(240px,380px)_1fr]">
                <div
                    ref={stageRef}
                    onPointerMove={move}
                    onPointerLeave={() => setDragging(null)}
                    className="relative mx-auto w-full max-w-[380px] overflow-hidden rounded-2xl bg-slate-950 shadow-xl ring-1 ring-black/10"
                    style={{ aspectRatio }}
                >
                    {scene.media_type === "video" || /\.(mp4|webm|mov)(\?|$)/i.test(mediaUrl || "") ? (
                        <video src={mediaUrl} className="h-full w-full object-cover" muted loop autoPlay playsInline />
                    ) : (
                        <img src={mediaUrl} alt={scene.title || content.title || "Scene preview"} className="h-full w-full object-cover" />
                    )}
                    <div className="absolute inset-x-0 bottom-0 h-[44%] bg-gradient-to-t from-black/80 to-transparent" />
                    {resolvedLogo && overlay("logo", <img src={resolvedLogo} alt="Brand logo" className="h-12 w-12 rounded-xl bg-white/90 object-contain p-1 shadow-lg sm:h-16 sm:w-16" />)}
                    {overlay("text", <span className="block max-w-[280px] rounded-lg bg-black/35 px-3 py-2 text-center text-base font-extrabold leading-tight text-white [text-shadow:0_2px_5px_#000] sm:text-xl">{scene.text || content.hook || content.title}</span>)}
                    {resolvedUsername && overlay("username", <span className="whitespace-nowrap rounded-lg bg-black/60 px-3 py-1.5 text-xs font-semibold text-white shadow">{resolvedUsername}</span>)}
                </div>

                <div className="space-y-4">
                    <label className="block rounded-xl border border-slate-200 bg-white p-4">
                        <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800"><Music size={17} /> Background music (optional)</span>
                        <input type="file" accept="audio/*" onChange={(event) => setMusic(event.target.files?.[0] || null)} className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-100 file:px-3 file:py-2 file:font-medium file:text-indigo-700" />
                        <span className="mt-2 block text-xs text-slate-500">Up to 25 MB. Music loops quietly beneath narration.</span>
                    </label>

                    <div className="flex flex-wrap gap-3">
                        <button type="button" disabled={busy} onClick={handleSave} className="inline-flex items-center gap-2 rounded-xl border border-indigo-200 bg-white px-4 py-2.5 text-sm font-semibold text-indigo-700 hover:bg-indigo-50 disabled:opacity-50"><Save size={17} /> Save layout</button>
                        <button type="button" disabled={busy} onClick={() => setLayout(DEFAULT_LAYOUT)} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"><RotateCcw size={17} /> Reset</button>
                        <button type="button" disabled={busy} onClick={handleRender} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"><Play size={17} /> {busy ? "Working…" : "Merge all scenes"}</button>
                    </div>

                    {message && <p className="rounded-xl bg-white px-4 py-3 text-sm text-slate-700" role="status">{message}</p>}
                    {renderUrl && (
                        <div className="rounded-xl bg-slate-950 p-3">
                            <video src={renderUrl} controls className="mx-auto max-h-[420px] w-full rounded-lg object-contain" />
                            <a href={renderUrl} download className="mt-3 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-900"><Download size={17} /> Download final MP4</a>
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
