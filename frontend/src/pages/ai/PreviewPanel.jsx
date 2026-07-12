import {
    Sparkles,
    Quote,
    FileText,
    Hash,
    Copy,
} from "lucide-react";

export default function PreviewPanel({ data }) {

    if (!data) {

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

                    Select your niche, choose a topic,
                    select a package and click

                    <span className="font-semibold text-blue-600">

                        {" "}Generate AI Content

                    </span>

                </p>

            </div>

        );

    }

    return (

        <div className="mt-10 space-y-6">

            {/* Header */}

            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl p-6">

                <h2 className="text-3xl font-bold">

                    {data.title}

                </h2>

                <p className="mt-3">

                    Niche : {data.niche}

                </p>

                <p>

                    Topic : {data.topic}

                </p>

                <p>

                    Package : {data.package}

                </p>

            </div>

            {/* Quote */}

            <div className="bg-white rounded-2xl shadow p-6">

                <div className="flex items-center gap-3 mb-4">

                    <Quote size={24} />

                    <h3 className="text-xl font-bold">

                        Quote

                    </h3>

                </div>

                <p className="text-gray-700">

                    {data.quote}

                </p>

            </div>

            {/* Caption */}

            <div className="bg-white rounded-2xl shadow p-6">

                <div className="flex items-center gap-3 mb-4">

                    <FileText size={24} />

                    <h3 className="text-xl font-bold">

                        Caption

                    </h3>

                </div>

                <p>

                    {data.caption}

                </p>

            </div>

            {/* Hashtags */}

            <div className="bg-white rounded-2xl shadow p-6">

                <div className="flex items-center gap-3 mb-4">

                    <Hash size={24} />

                    <h3 className="text-xl font-bold">

                        Hashtags

                    </h3>

                </div>

                <div className="flex flex-wrap gap-2">

                    <span className="bg-blue-100 px-3 py-1 rounded-full">

                        #viral

                    </span>

                    <span className="bg-blue-100 px-3 py-1 rounded-full">

                        #motivation

                    </span>

                    <span className="bg-blue-100 px-3 py-1 rounded-full">

                        #ai

                    </span>

                </div>

            </div>

            {/* Copy */}

            <div className="text-right">

                <button
                    className="bg-blue-600 text-white px-5 py-3 rounded-xl flex items-center gap-2 ml-auto"
                >

                    <Copy size={18} />

                    Copy Content

                </button>

            </div>

        </div>

    );

}