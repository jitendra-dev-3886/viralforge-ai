import { useEffect, useMemo, useRef, useState } from "react";
import { Download, Grip, Music, Play, RotateCcw, Save } from "lucide-react";
import { updateContent } from "../../api/content";
import { generateProjectRender, uploadProjectMusic } from "../../api/projectRender";
import { assetUrl } from "../../api/axios";
import api from "../../api/axios";
import { downloadMedia } from "../../api/media";
import { StyleFrame, StyledCaption, StyledLogo } from "./StyleArtwork";
import { getVisualStyle, getDefaultLayout, getSavedLayout, mediaPlacement, VISUAL_STYLES } from "./visualStyles";

import PlatformUsername from "./PlatformUsername";

const clamp = (value) => Math.max(3, Math.min(97, value));

export default function ContentFinisher({ content, brandName: projectBrandName = "", logo = "", projectId, onBusyChange, disableBackgroundMusic = false }) {
    const [styleId, setStyleId] = useState(content.generation_config?.visual_style || "");
    const preset = getVisualStyle(styleId);
    const defaultLayout = getDefaultLayout(preset);
    const [opacity, setOpacity] = useState(content.generation_config?.overlay_opacity || {});
    const stageRef = useRef(null);
    const [layout, setLayout] = useState(() => getSavedLayout(preset, content.generation_config));
    const [dragging, setDragging] = useState(null);
    const [music, setMusic] = useState(null);
    const [busy, setBusy] = useState(false);
    useEffect(() => { onBusyChange?.(busy); }, [busy, onBusyChange]);
    const [message, setMessage] = useState("");
    const [renderUrl, setRenderUrl] = useState("");

    const [sceneIndex, setSceneIndex] = useState(0);
    const scene = content.scenes?.[sceneIndex];
    const isImageContent = content.scenes?.length > 0 && content.scenes.every((item) => item.media_type === "image");
    const mediaUrl = assetUrl(scene?.media_url);
    const resolvedLogo = assetUrl(logo || content.branding?.logo || content.generation_config?.branding?.logo);
    const [brandName, setBrandName] = useState(content.generation_config?.branding?.brand_name || content.branding?.brand_name || projectBrandName || "");
    const resolvedUsername = brandName;
    const contentId = content.id || content.content_id;
    const resolvedProjectId = projectId || content.project_id;
    const aspectRatio = useMemo(() => {
        const type = String(content.content_type || "").toLowerCase();
        const platform = String(content.platform || "").toLowerCase();
        if (/reel|short|story/.test(type)) return "9 / 16";
        if (type.includes("carousel") && platform.includes("instagram")) return "4 / 5";
        if (platform.includes("youtube") && type.includes("video")) return "16 / 9";
        if (platform.includes("instagram")) return "4 / 5";
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
                ...(disableBackgroundMusic ? { audio: { ...content.generation_config?.audio, music_id: null, license_note: "" } } : {}),
                visual_style: styleId || null,
                visual_layout_version: 2,
                overlay_opacity: opacity,
                branding: {
                    ...(content.generation_config?.branding || content.branding || {}),
                    brand_name: brandName,
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
        if (!disableBackgroundMusic && music && music.size > 25 * 1024 * 1024) {
            setMessage("Background music must be 25 MB or smaller.");
            return;
        }
        setBusy(true);
        setMessage("Saving layout and rendering all scenes…");
        try {
            await saveLayout();
            if (!disableBackgroundMusic && music) await uploadProjectMusic(resolvedProjectId, music);
            const result = await generateProjectRender(resolvedProjectId, contentId);
            const url = result.file_url || result.output_url || result.render?.file_url;
            const freshUrl = assetUrl(url);
            setRenderUrl(freshUrl ? `${freshUrl}${freshUrl.includes("?") ? "&" : "?"}v=${Date.now()}` : "");
            setMessage("Final video created with your saved visual and audio settings.");
        } catch (error) {
            setMessage(error.response?.data?.detail || error.message || "Unable to create the final render.");
        } finally {
            setBusy(false);
        }
    };

    const handleImageExport = async () => {
        setBusy(true);
        setMessage("Saving layout and exporting styled images...");
        try {
            if (content.scenes.some((item) => !item.id || !item.media_url)) throw new Error("Every slide needs saved media before exporting. Regenerate missing media first.");
            await saveLayout();
            const response = await api.post("/render/images", { scene_ids: content.scenes.map((item) => item.id) }, { headers: { "Idempotency-Key": crypto.randomUUID() } });
            const ids = response.data.media_ids;
            await downloadMedia(ids);
            setMessage("Styled PNG images exported with your saved layout.");
        } catch (error) {
            setMessage(error.response?.data?.detail || error.message || "Unable to export images.");
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
            style={{ left: `${layout[name]?.x ?? defaultLayout[name].x}%`, top: `${layout[name]?.y ?? defaultLayout[name].y}%`, transform: "translate(-50%, -50%)", ...(preset ? { width: name === "logo" ? `min(${preset.logo.size * 100}cqw, ${preset.logo.size * 100}cqh)` : `${preset[name].width * 100}%` } : name === "text" ? { width: "84%" } : {}) }}
            aria-label={`Drag ${name} overlay`}
        >
            {children}
        </button>
    );

    return (
        <section className="mt-8 rounded-2xl border border-indigo-200 bg-indigo-50/60 p-4 sm:p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h3 className="text-lg font-bold text-slate-900">Finish & export{preset ? ` · ${preset.name}` : ""}</h3>
                    <p className="text-sm text-slate-600">Drag the text, logo, and brand name. The layout applies to every scene in your final export.</p>
                </div>
                <Grip className="text-indigo-500" size={22} />
            </div>

            <div className="grid gap-6 lg:grid-cols-[minmax(240px,380px)_1fr]">
                <div
                    ref={stageRef}
                    data-style-stage
                    onPointerMove={move}
                    onPointerLeave={() => setDragging(null)}
                    className="relative mx-auto w-full max-w-[380px] overflow-hidden rounded-2xl bg-slate-950 shadow-xl ring-1 ring-black/10"
                    style={{ aspectRatio, containerType: "size" }}
                >
                    {scene.media_type === "video" || /\.(mp4|webm|mov)(\?|$)/i.test(mediaUrl || "") ? (
                        <video src={mediaUrl} style={mediaPlacement(preset)} muted loop autoPlay playsInline />
                    ) : (
                        <img src={mediaUrl} alt={scene.title || content.title || "Scene preview"} style={mediaPlacement(preset)} />
                    )}
                    {preset ? <StyleFrame preset={preset} /> : <div className="absolute inset-x-0 bottom-0 h-[44%] bg-black/50" />}
                    {preset?.logo.visible !== false && resolvedLogo && overlay("logo", preset ? <StyledLogo preset={preset} src={resolvedLogo} opacity={opacity.logo} /> : <img src={resolvedLogo} alt="Brand logo" className="h-12 w-12 rounded-xl bg-white/90 object-contain p-1 shadow-lg sm:h-16 sm:w-16" />)}
                    {overlay("text", preset ? <StyledCaption preset={preset} text={scene.text || content.hook || content.title} opacity={opacity.text} /> : <span className="inline-block whitespace-pre-wrap rounded-lg bg-black/50 px-3 py-2 text-center text-base font-bold leading-relaxed text-white">{scene.text || content.hook || content.title}</span>)}
                    {preset?.username.visible !== false && resolvedUsername && overlay("username", <PlatformUsername preset={preset} text={resolvedUsername} platform={content.platform} opacity={opacity.username} />)}
                </div>

                <div className="space-y-4">
                    <label className="block text-sm font-semibold text-slate-800">Design layout
                        <select disabled={busy} value={styleId} onChange={(event) => { setStyleId(event.target.value); setLayout(getDefaultLayout(getVisualStyle(event.target.value))); setRenderUrl(""); setMessage("Design changed. Export again to apply it."); }} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white p-3">
                            {!styleId && <option value="">Original layout</option>}
                            {VISUAL_STYLES.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                        </select>
                        <span className="mt-2 block text-xs font-normal text-slate-500">Changing the design applies its logo, brand name and text positions. You can then drag to adjust.</span>
                    </label>
                    <label className="block text-sm font-semibold text-slate-800">Brand name
                        <input disabled={busy} value={brandName} onChange={(event) => { setBrandName(event.target.value); setRenderUrl(""); }} className="mt-2 w-full rounded-xl border border-slate-200 p-3" placeholder="Your brand name" />
                        <span className="mt-1 block text-xs font-normal text-slate-500">Use your full brand name. Save layout to apply it to exports.</span>
                    </label>
                    <label className="block text-sm font-semibold text-slate-800">Preview scene
                        <select value={sceneIndex} onChange={(event) => setSceneIndex(Number(event.target.value))} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white p-3">
                            {content.scenes.map((item, index) => <option key={item.id || index} value={index}>Scene {index + 1}</option>)}
                        </select>
                    </label>
                    {preset && <fieldset disabled={busy} className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
                        <legend className="px-1 text-sm font-semibold text-slate-800">Overlay opacity</legend>
                        {[['logo', 'Logo'], ['username', 'Brand name'], ['text', 'Text']].filter(([name]) => preset[name].visible !== false).map(([name, label]) => <label key={name} className="block text-xs text-slate-600">
                            <span className="flex justify-between"><span>{label}</span><span>{Math.round((opacity[name] ?? preset[name].opacity ?? 1) * 100)}%</span></span>
                            <input aria-label={`${label} opacity`} type="range" min="0" max="100" value={Math.round((opacity[name] ?? preset[name].opacity ?? 1) * 100)} onChange={(event) => { setOpacity((current) => ({ ...current, [name]: Number(event.target.value) / 100 })); setRenderUrl(""); }} className="mt-1 w-full accent-indigo-600" />
                        </label>)}
                    </fieldset>}
                    <p className="text-xs text-slate-500">Layout preview. Text fits automatically in the exported file.</p>
                    {!disableBackgroundMusic && <label className="block rounded-xl border border-slate-200 bg-white p-4">
                        <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800"><Music size={17} /> Background music (optional)</span>
                        <input type="file" accept="audio/*" onChange={(event) => setMusic(event.target.files?.[0] || null)} className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-100 file:px-3 file:py-2 file:font-medium file:text-indigo-700" />
                        <span className="mt-2 block text-xs text-slate-500">Up to 25 MB. Music loops quietly beneath narration in video exports.</span>
                    </label>}

                    <div className="flex flex-wrap gap-3">
                        <button type="button" disabled={busy} onClick={handleSave} className="inline-flex items-center gap-2 rounded-xl border border-indigo-200 bg-white px-4 py-2.5 text-sm font-semibold text-indigo-700 hover:bg-indigo-50 disabled:opacity-50"><Save size={17} /> Save layout</button>
                        <button type="button" disabled={busy} onClick={() => setLayout(defaultLayout)} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"><RotateCcw size={17} /> {preset ? "Use preset positions" : "Reset"}</button>
                        <button type="button" disabled={busy} onClick={isImageContent ? handleImageExport : handleRender} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"><Play size={17} /> {busy ? "Working…" : isImageContent ? "Export styled images" : "Merge all scenes"}</button>
                        {isImageContent && <button type="button" disabled={busy} onClick={handleRender} className="rounded-xl border border-indigo-200 bg-white px-4 py-2.5 text-sm font-semibold text-indigo-700 disabled:opacity-50">Merge as video</button>}
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
