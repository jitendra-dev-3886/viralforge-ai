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

            return (
                <div className="mt-6">
                    <strong>Scenes</strong>
                    <div className="mt-4 space-y-4">
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
                                </div>
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
                </div>
            </div>
        );
    };

    const renderPlatformContent = () => (
        <div className="space-y-8 mt-8">
            {Object.entries(data.data).map(([platform, platformData]) => (
                <div
                    key={platform}
                    className="bg-white rounded-3xl shadow-lg p-8"
                >
                    <h2 className="text-3xl font-bold capitalize text-indigo-600 mb-8">
                        {platform.replace("_", " ")}
                    </h2>
                    {Object.entries(platformData).map(([type, content]) => {
                        const videoText = content.video || content.script || content.voiceover || "";
                        const voiceoverText = content.voiceover || content.script || "";
                        const hashtags = normalizeArray(content.hashtags);

                        return (
                            <div
                                key={type}
                                className="border rounded-2xl p-6 mb-6 bg-slate-50"
                            >
                                <h3 className="text-xl font-bold capitalize mb-6">
                                    {type}
                                </h3>
                                <div className="space-y-5">
                                    <div>
                                        <strong>
                                            Video
                                        </strong>
                                        <p className="mt-2 text-gray-700">
                                            {videoText}
                                        </p>
                                    </div>
                                    <div>
                                        <strong>
                                            Voiceover
                                        </strong>
                                        <p className="mt-2 text-gray-700">
                                            {voiceoverText}
                                        </p>
                                    </div>
                                    <div>
                                        <strong>
                                            Caption
                                        </strong>
                                        <p className="mt-2 text-gray-700">
                                            {content.caption}
                                        </p>
                                    </div>
                                    <div>
                                        <strong>
                                            Hashtags
                                        </strong>
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
                                </div>
                            <button
                                onClick={() => copyContent(content)}
                                className="mt-8 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl flex items-center gap-2"
                            >
                                <Copy size={18} />
                                Copy Content
                            </button>
                        </div>
                    );
                })}
                </div>
            ))}
        </div>
    );

    const isFlatResponse = data.data && data.data.title !== undefined;

    if (isFlatResponse) {
        return <div className="mt-8">{renderContentCard(data.data)}</div>;
    }

    return renderPlatformContent();
}
