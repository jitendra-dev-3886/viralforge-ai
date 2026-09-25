import { useEffect, useState } from "react";
import { Copy, Download, Sparkles } from "lucide-react";
import { downloadMedia } from "../../api/media";
import ContentFinisher from "./ContentFinisher";
import SceneMediaUpload from "../../components/SceneMediaUpload";
import { assetUrl } from "../../api/axios";
import { Link } from "react-router-dom";
import { getContent } from "../../api/content";

export default function PreviewPanel({ data, username = "", brandName = "", logo = "", projectId }) {
    const [uploads, setUploads] = useState({});
    const [uploadBusy, setUploadBusy] = useState(false);
    const [selectedMediaIds, setSelectedMediaIds] = useState([]);
    const [downloading, setDownloading] = useState(false);
    const [downloadError, setDownloadError] = useState("");
    const [savedContents, setSavedContents] = useState({});
    const [sceneError, setSceneError] = useState("");

    useEffect(() => {
        setUploads({});
        setSelectedMediaIds([]);
        setDownloadError("");
        setSavedContents({});
        setSceneError("");
        let active = true;
        const outputs = data?.data?.title !== undefined
            ? [{ ...data.data, content_id: data.data.content_id || data.content_id }]
            : Object.values(data?.data || {}).flatMap(platform => Object.values(platform || {}));
        const missing = outputs.filter(content => (content?.content_id || content?.id) &&
            (!content.scenes?.length || content.scenes.some(scene => !scene.id)));
        Promise.all(missing.map(async content => {
            const id = content.content_id || content.id;
            const response = await getContent(id);
            const saved = response.content || response.data || response;
            if (!saved.scenes?.length) throw new Error("Saved scenes are unavailable.");
            return [id, saved];
        })).then(entries => { if (active) setSavedContents(Object.fromEntries(entries)); })
            .catch(() => { if (active) setSceneError("Unable to load saved scenes. Open the content editor or refresh to try again."); });
        return () => { active = false; };
    }, [data]);

    const normalizeArray = (value) => {
        if (!value) return [];
        if (Array.isArray(value)) {
            return value.map((item) => String(item).trim()).filter(Boolean);
        }
        return String(value)
            .split(/[,\n]+/)
            .map((item) => item.trim())
            .filter(Boolean);
    };

    const normalizeMediaIds = (mediaIds) => [
        ...new Set(mediaIds.filter((mediaId) => Number.isInteger(mediaId))),
    ];

    const sceneMediaIds = (scenes = []) => (
        normalizeMediaIds(scenes.map((scene) => scene.media_id))
    );

    const toggleMedia = (mediaId) => {
        if (!Number.isInteger(mediaId)) return;

        setSelectedMediaIds((current) => (
            current.includes(mediaId)
                ? current.filter((id) => id !== mediaId)
                : [...current, mediaId]
        ));
    };

    const toggleGroup = (scenes) => {
        const mediaIds = sceneMediaIds(scenes);
        if (!mediaIds.length) return;

        setSelectedMediaIds((current) => {
            const everySelected = mediaIds.every((mediaId) => current.includes(mediaId));
            return everySelected
                ? current.filter((mediaId) => !mediaIds.includes(mediaId))
                : normalizeMediaIds([...current, ...mediaIds]);
        });
    };

    const handleDownload = async (mediaIds = selectedMediaIds) => {
        const ids = normalizeMediaIds(mediaIds);
        if (!ids.length) return;

        setDownloading(true);
        setDownloadError("");
        try {
            await downloadMedia(ids);
        } catch (error) {
            console.error("Media download failed", error);
            setDownloadError("Unable to download the selected media. Please try again.");
        } finally {
            setDownloading(false);
        }
    };

    const copyContent = (content) => {
        const text = [
            `Title:\n${content.title || ""}`,
            `Description:\n${content.description || ""}`,
            `Voiceover:\n${content.script || ""}`,
            `Caption:\n${content.caption || ""}`,
            `Hashtags:\n${normalizeArray(content.hashtags).join(" ")}`,
            `Keywords:\n${normalizeArray(content.keywords).join(", ")}`,
            `CTA:\n${content.cta || ""}`,
        ].join("\n\n");
        navigator.clipboard.writeText(text);
    };

    const renderScene = (scene, index) => {
        const mediaId = scene.media_id;
        const canDownload = Number.isInteger(mediaId);
        const checked = canDownload && selectedMediaIds.includes(mediaId);

        return (
            <article key={`${scene.scene || index}-${mediaId || "pending"}`} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            aria-label={`Select scene ${scene.scene || index + 1}`}
                            checked={checked}
                            disabled={!canDownload}
                            onChange={() => toggleMedia(mediaId)}
                            className="h-4 w-4 accent-blue-600 disabled:cursor-not-allowed"
                        />
                        <div>
                            <p className="text-sm font-semibold text-slate-800">
                                Scene {scene.scene || index + 1}
                            </p>
                            <p className="text-xs capitalize text-slate-500">
                                {scene.media_type || "image"}
                            </p>
                        </div>
                    </div>
                    {canDownload && (
                        <button
                            type="button"
                            onClick={() => handleDownload([mediaId])}
                            disabled={downloading}
                            className="inline-flex items-center gap-1 rounded-lg border border-blue-200 px-3 py-2 text-xs font-medium text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            <Download size={15} />
                            Download source
                        </button>
                    )}
                </div>

                <div className="mt-3 space-y-2 text-sm text-slate-700">
                    {scene.text && <p><strong>Text:</strong> {scene.text}</p>}
                    {scene.keyword && <p><strong>Visual:</strong> {scene.keyword}</p>}
                    {scene.media_provider && <p><strong>Source:</strong> {scene.media_provider}</p>}
                </div>

                {scene.media_url && (
                    scene.media_type === "video" ? (
                        <video
                            className="mt-4 max-h-80 w-full rounded-xl bg-slate-950 object-contain"
                            controls
                            preload="metadata"
                            src={assetUrl(scene.media_url)}
                        >
                            Your browser cannot preview this video.
                        </video>
                    ) : (
                        <img
                            className="mt-4 max-h-80 w-full rounded-xl object-cover"
                            src={assetUrl(scene.media_url)}
                            alt={scene.keyword || `Scene ${scene.scene || index + 1}`}
                        />
                    )
                )}

                {!scene.media_url && (
                    <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
                        Media preview is unavailable for this scene. Regenerate after checking Pexels/Pixabay API keys.
                    </p>
                )}
                <SceneMediaUpload sceneId={scene.id} disabled={uploadBusy} onBusyChange={setUploadBusy} onUploaded={result => { setUploads(current => ({...current, [scene.id]: result})); setSelectedMediaIds(current => current.filter(id => id !== scene.media_id)); }} />
            </article>
        );
    };

    const renderScenes = (content) => {
        const scenes = content.scenes || [];
        if (!scenes.length) return null;

        const mediaIds = sceneMediaIds(scenes);
        const allSelected = mediaIds.length > 0 && mediaIds.every((id) => selectedMediaIds.includes(id));
        const isCarousel = content.content_type?.toLowerCase().includes("carousel")
            || (Boolean(content.story) && scenes.every((scene) => (scene.media_type || "image") === "image"));

        return (
            <section className="mt-7 border-t border-slate-200 pt-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h3 className="font-semibold text-slate-900">
                            {isCarousel ? "Carousel slides" : "Scene media"}
                        </h3>
                        <p className="mt-1 text-xs text-slate-500">
                            These are source assets. Use Finish & export below for your styled output.
                        </p>
                    </div>
                    {mediaIds.length > 0 && (
                        <div className="flex items-center gap-3">
                            <label className="flex cursor-pointer items-center gap-2 text-xs font-medium text-slate-700">
                                <input
                                    type="checkbox"
                                    checked={allSelected}
                                    onChange={() => toggleGroup(scenes)}
                                    className="h-4 w-4 accent-blue-600"
                                />
                                Select all
                            </label>
                            <button
                                type="button"
                                onClick={() => handleDownload(mediaIds)}
                                disabled={downloading}
                                className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                <Download size={15} />
                                Download all sources
                            </button>
                        </div>
                    )}
                </div>
                <div className={`mt-4 ${isCarousel ? "grid gap-4 sm:grid-cols-2" : "space-y-4"}`}>
                    {scenes.map(renderScene)}
                </div>
            </section>
        );
    };

    const renderContentCard = (original) => {
        const contentId = original.content_id || original.id;
        const saved = savedContents[contentId] || original;
        const content = {...original, ...saved, scenes: (saved.scenes || []).map(scene => uploads[scene.id] ? {...scene, ...uploads[scene.id]} : scene)};
        const hashtags = normalizeArray(content.hashtags);
        const keywords = normalizeArray(content.keywords);

        return (
            <article className="rounded-3xl bg-white p-6 shadow-lg sm:p-8">
                <div className="space-y-5">
                    <div>
                        <h2 className="text-2xl font-bold text-indigo-600">{content.title || "Generated content"}</h2>
                        {content.description && <p className="mt-2 text-slate-600">{content.description}</p>}
                    </div>
                    {content.hook && <div><strong>Hook</strong><p className="mt-1 text-slate-700">{content.hook}</p></div>}
                    {content.story && <div><strong>Carousel story</strong><p className="mt-1 text-slate-700">{content.story}</p></div>}
                    {content.script && <div><strong>Voiceover</strong><p className="mt-1 whitespace-pre-line text-slate-700">{content.script}</p></div>}
                    {content.caption && <div><strong>Caption</strong><p className="mt-1 whitespace-pre-line text-slate-700">{content.caption}</p></div>}
                    {keywords.length > 0 && <div><strong>Keywords</strong><div className="mt-2 flex flex-wrap gap-2">{keywords.map((keyword) => <span key={keyword} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-800">{keyword}</span>)}</div></div>}
                    {hashtags.length > 0 && <div><strong>Hashtags</strong><div className="mt-2 flex flex-wrap gap-2">{hashtags.map((tag) => <span key={tag} className="rounded-full bg-indigo-100 px-3 py-1 text-sm text-indigo-700">{tag}</span>)}</div></div>}
                    {content.cta && <div><strong>Call to action</strong><p className="mt-1 text-slate-700">{content.cta}</p></div>}
                </div>

                <button type="button" onClick={() => copyContent(content)} className="mt-7 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-white hover:bg-indigo-700">
                    <Copy size={18} />
                    Copy content
                </button>

                {renderScenes(content)}
                {contentId && <Link to={`/content/${contentId}/edit`} className="mt-4 inline-block rounded-xl border border-indigo-200 px-4 py-2 text-sm font-semibold text-indigo-700">Open content editor · Upload scene media</Link>}
                <fieldset disabled={uploadBusy}><ContentFinisher
                    content={content}
                    username={username}
                    brandName={brandName}
                    logo={logo}
                    projectId={projectId || content.project_id}
                /></fieldset>
            </article>
        );
    };

    if (!data?.data) {
        return (
            <div className="mt-10 rounded-2xl bg-white p-10 text-center shadow-lg">
                <Sparkles size={70} className="mx-auto text-blue-500" />
                <h2 className="mt-6 text-3xl font-bold">AI Content Preview</h2>
                <p className="mt-4 text-gray-500">Generate content first. Each scene in the preview will include an optional image or video upload.</p>
                <Link to="/history" className="mt-4 inline-block text-sm text-indigo-600 underline">Open saved content to upload media</Link>
            </div>
        );
    }

    const isFlatResponse = data.data.title !== undefined;

    return (
        <div className="mt-8 space-y-8">
            {selectedMediaIds.length > 0 && (
                <div className="sticky top-4 z-10 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-blue-200 bg-blue-50 p-4 shadow-sm">
                    <p className="text-sm font-medium text-blue-900">
                        {selectedMediaIds.length} asset{selectedMediaIds.length === 1 ? "" : "s"} selected
                    </p>
                    <button
                        type="button"
                        onClick={() => handleDownload()}
                        disabled={downloading}
                        className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        <Download size={17} />
                        {downloading ? "Preparing download..." : "Download selected"}
                    </button>
                </div>
            )}

            {downloadError && <p className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{downloadError}</p>}
            {sceneError && <p role="alert" className="rounded-xl bg-amber-50 p-3 text-sm text-amber-800">{sceneError}</p>}

            {isFlatResponse ? renderContentCard({ ...data.data, content_id: data.data.content_id || data.content_id }) : (
                Object.entries(data.data).map(([platform, platformData]) => (
                    <section key={platform} className="space-y-5">
                        <h2 className="text-3xl font-bold capitalize text-indigo-600">{platform.replaceAll("_", " ")}</h2>
                        {Object.entries(platformData).map(([type, content]) => (
                            <div key={type} className="space-y-3">
                                <h3 className="text-xl font-bold capitalize text-slate-800">{type.replaceAll("_", " ")}</h3>
                                {renderContentCard(content)}
                            </div>
                        ))}
                    </section>
                ))
            )}
        </div>
    );
}
