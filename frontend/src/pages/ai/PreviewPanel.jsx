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

    return (

        <div className="space-y-8 mt-8">

            {data.data.map((platform) => (

                <div
                    key={platform.platform}
                    className="bg-white rounded-3xl shadow-lg p-8"
                >

                    <h2 className="text-3xl font-bold capitalize text-indigo-600 mb-8">

                        {platform.platform}

                    </h2>

                    {platform.contents.map((content, index) => (

                        <div
                            key={index}
                            className="border rounded-2xl p-6 mb-6 bg-slate-50"
                        >

                            <h3 className="text-xl font-bold capitalize mb-6">

                                {content.type}

                            </h3>

                            <div className="space-y-5">

                                <div>

                                    <strong>Title</strong>

                                    <p>{content.title}</p>

                                </div>

                                <div>

                                    <strong>Hook</strong>

                                    <p>{content.hook}</p>

                                </div>

                                <div>

                                    <strong>Script</strong>

                                    <p>{content.script}</p>

                                </div>

                                <div>

                                    <strong>Caption</strong>

                                    <p>{content.caption}</p>

                                </div>

                                <div>

                                    <strong>Hashtags</strong>

                                    <div className="flex flex-wrap gap-2 mt-2">

                                        {content.hashtags.map((tag) => (

                                            <span
                                                key={tag}
                                                className="bg-indigo-100 px-3 py-1 rounded-full text-sm"
                                            >
                                                {tag}
                                            </span>

                                        ))}

                                    </div>

                                </div>

                                <div>

                                    <strong>Image Prompt</strong>

                                    <p>{content.image_prompt}</p>

                                </div>

                                <div>

                                    <strong>Video Prompt</strong>

                                    <p>{content.video_prompt}</p>

                                </div>

                                <div>

                                    <strong>Voiceover</strong>

                                    <p>{content.voiceover}</p>

                                </div>

                            </div>

                            <button className="mt-8 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl flex items-center gap-2">

                                <Copy size={18} />

                                Copy Content

                            </button>

                        </div>

                    ))}

                </div>

            ))}

        </div>

    );

}