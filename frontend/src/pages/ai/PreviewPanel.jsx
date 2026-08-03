import {
    Sparkles,
    Copy,
} from "lucide-react";

export default function PreviewPanel({ data }) {

    if (!data || !data.data) {
        return (
            <div className="mt-10 bg-white rounded-2xl shadow-lg p-10 text-center">
                <Sparkles
                    size={70}
                    className="mx-auto text-blue-500"
                />

                <h2 className="text-3xl font-bold mt-6">
                    AI Content Preview
                </h2>

                <p className="text-gray-500 mt-4">
                    Generate content to preview results.
                </p>
            </div>
        );
    }

    const normalizeArray = (value) => {
        if (!value) {
            return [];
        }

        if (Array.isArray(value)) {
            return value.map((item) => String(item).trim()).filter(Boolean);
        }

        return String(value)
            .split(/[,\n]+/)
            .map((item) => item.trim())
            .filter(Boolean);
    };

    const copyContent = (content) => {
        const hashtags = normalizeArray(content.hashtags).join(" ");
        const keywords = normalizeArray(content.keywords).join(", ");

        const text = `
Title:
${content.title}

Description:
${content.description || ""}

Voiceover:
${content.script}

Caption:
${content.caption}

Hashtags:
${hashtags}

Keywords:
${keywords}

CTA:
${content.cta || ""}
        `;

        navigator.clipboard.writeText(text);
    };

    const renderContentCard = (content) => {
        const hashtags = normalizeArray(content.hashtags);
        const keywords = normalizeArray(content.keywords);

        const renderScenes = () => {
            if (!content.scenes || content.scenes.length === 0) {
                return null;
            }

            const isCarousel = Boolean(content.story) && content.scenes.every(
                (scene) => (scene.media_type || "image") === "image",
            );

            return (
                <div className="mt-6">
                    <strong>{isCarousel ? "Carousel slides" : "Scene media"}</strong>
                    <div className={`mt-4 ${isCarousel ? "grid gap-4 sm:grid-cols-2" : "space-y-4"}`}>
                        {content.scenes.map((scene, index) => (
                            <div
                                key={index}
                                className="border rounded-2xl p-4 bg-white"
                            >
                                <div className="flex flex-wrap gap-4">
                                    <span className="text-sm font-semibold text-slate-700">
                                        Scene {scene.scene || index + 1}
                                    </span>
                                    <span className="text-sm text-slate-500">
                                        {scene.media_type || "image"}
                                    </span>
                                </div>
                                <div className="mt-3 space-y-2 text-sm text-slate-700">
                                    {scene.text && (
                                        <p>
                                            <strong>Text:</strong> {scene.text}
                                        </p>
                                    )}
                                    {scene.keyword && (
                                        <p>
                                            <strong>Keyword:</strong> {scene.keyword}
                                        </p>
                                    )}
                                    {scene.image_prompt && (
                                        <p>
                                            <strong>Image Prompt:</strong> {scene.image_prompt}
                                        </p>
                                    )}
                                    {scene.video_prompt && (
                                        <p>
                                            <strong>Video Prompt:</strong> {scene.video_prompt}</p>
                                    )}
                                    {scene.media_provider && (
                                        <p>
                                            <strong>Source:</strong> {scene.media_provider}
                                        </p>
                                    )}
                                </div>
                                {scene.media_url && (
                                    scene.media_type === "video" ? (
                                        <video
                                            className="mt-4 max-h-80 w-full rounded-xl bg-slate-950 object-contain"
                                            controls
                                            preload="metadata"
                                            src={scene.media_url}
                                        >
                                            Your browser cannot preview this video.
                                        </video>
                                    ) : (
                                        <img
                                            className="mt-4 max-h-80 w-full rounded-xl object-cover"
                                            src={scene.media_url}
                                            alt={scene.keyword || `Scene ${scene.scene || index + 1}`}
                                        />
                                    )
                                )}
                                {!scene.media_url && (
                                    <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
                                        Media preview is unavailable for this scene. Check your Pexels/Pixabay API keys, then regenerate this content.
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            );
        };

        return (
            <div className="bg-white rounded-3xl shadow-lg p-8">
                <h2 className="text-3xl font-bold capitalize text-indigo-600 mb-6">
                    Generated Content
                </h2>

                <div className="border rounded-2xl p-6 mb-6 bg-slate-50">
                    <div className="space-y-5">
                        <div>
                            <strong>Title</strong>
                            <p className="mt-2 text-gray-700">{content.title}</p>
                        </div>
                        {content.description && (
                            <div>
                                <strong>Description</strong>
                                <p className="mt-2 text-gray-700">{content.description}</p>
                            </div>
                        )}
                        {content.hook && (
                            <div>
                                <strong>Hook</strong>
                                <p className="mt-2 text-gray-700">{content.hook}</p>
                            </div>
                        )}
                        {content.story && (
                            <div>
                                <strong>Carousel Story</strong>
                                <p className="mt-2 text-gray-700">{content.story}</p>
                            </div>
                        )}
                        <div>
                            <strong>Voiceover</strong>
                            <p className="mt-2 text-gray-700">{content.script}</p>
                        </div>
                        <div>
                            <strong>Caption</strong>
                            <p className="mt-2 text-gray-700">{content.caption}</p>
                        </div>
                        {keywords.length > 0 && (
                            <div>
                                <strong>Keywords</strong>
                                <div className="flex flex-wrap gap-2 mt-3">
                                    {keywords.map((keyword, index) => (
                                        <span
                                            key={index}
                                            className="bg-slate-100 text-slate-800 px-3 py-1 rounded-full text-sm"
                                        >
                                            {keyword}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {hashtags.length > 0 && (
                            <div>
                                <strong>Hashtags</strong>
                                <div className="flex flex-wrap gap-2 mt-3">
                                    {hashtags.map((tag, index) => (
                                        <span
                                            key={index}
                                            className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {content.cta && (
                            <div>
                                <strong>Call to Action</strong>
                                <p className="mt-2 text-gray-700">{content.cta}</p>
                            </div>
                        )}
                    </div>

                    <button
                        onClick={() => copyContent(content)}
                        className="mt-8 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl flex items-center gap-2"
                    >
                        <Copy size={18} />
                        Copy Content
                    </button>

                    {renderScenes()}
                </div>
            </div>
        );
    };

    const renderPlatformContent = () => (
        <div className="space-y-8 mt-8">
            {Object.entries(data.data).map(([platform, platformData]) => (
                <section key={platform}>
                    <h2 className="mb-5 text-3xl font-bold capitalize text-indigo-600">
                        {platform.replaceAll("_", " ")}
                    </h2>
                    <div className="space-y-6">
                        {Object.entries(platformData).map(([type, content]) => (
                            <div key={type}>
                                <h3 className="mb-3 text-xl font-bold capitalize text-slate-800">
                                    {type.replaceAll("_", " ")}
                                </h3>
                                {renderContentCard(content)}
                            </div>
                        ))}
                    </div>
                </section>
            ))}
        </div>
    );

    const isFlatResponse = data.data && data.data.title !== undefined;

    if (isFlatResponse) {
        return <div className="mt-8">{renderContentCard(data.data)}</div>;
    }

    return renderPlatformContent();
}
