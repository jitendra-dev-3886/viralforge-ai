import { useState } from "react";
import {
    Sparkles,
    Wand2,
    Languages,
    FileText,
    Copy,
    Download,
    RotateCcw
} from "lucide-react";

export default function AIGenerator() {

    const [contentType, setContentType] = useState("instagram");
    const [tone, setTone] = useState("professional");
    const [language, setLanguage] = useState("English");
    const [prompt, setPrompt] = useState("");

    return (

        <div className="min-h-screen bg-slate-100 p-8">

            <div className="max-w-7xl mx-auto">

                {/* Header */}

                <div className="flex justify-between items-center mb-8">

                    <div>

                        <h1 className="text-4xl font-bold text-slate-900">
                            AI Content Generator
                        </h1>

                        <p className="text-slate-500 mt-2">
                            Generate high-quality AI content for every platform.
                        </p>

                    </div>

                    <div className="bg-white rounded-xl shadow px-6 py-4">

                        <p className="text-sm text-slate-500">
                            Credits Remaining
                        </p>

                        <h2 className="text-3xl font-bold text-blue-600">
                            985
                        </h2>

                    </div>

                </div>

                <div className="grid lg:grid-cols-3 gap-8">

                    {/* Left */}

                    <div className="lg:col-span-1">

                        <div className="bg-white rounded-2xl shadow p-6">

                            <h3 className="text-xl font-semibold mb-6">
                                Content Settings
                            </h3>

                            <label className="font-medium">
                                Template
                            </label>

                            <select
                                className="w-full mt-2 border rounded-xl p-3"
                                value={contentType}
                                onChange={(e)=>setContentType(e.target.value)}
                            >

                                <option value="instagram">Instagram Caption</option>
                                <option value="facebook">Facebook Post</option>
                                <option value="linkedin">LinkedIn Post</option>
                                <option value="twitter">X (Twitter)</option>
                                <option value="blog">Blog Article</option>
                                <option value="youtube">YouTube Script</option>
                                <option value="reel">Reel Script</option>

                            </select>

                            <label className="font-medium mt-6 block">
                                Tone
                            </label>

                            <select
                                className="w-full mt-2 border rounded-xl p-3"
                                value={tone}
                                onChange={(e)=>setTone(e.target.value)}
                            >

                                <option>Professional</option>
                                <option>Funny</option>
                                <option>Friendly</option>
                                <option>Luxury</option>
                                <option>Sales</option>

                            </select>

                            <label className="font-medium mt-6 block">
                                Language
                            </label>

                            <select
                                className="w-full mt-2 border rounded-xl p-3"
                                value={language}
                                onChange={(e)=>setLanguage(e.target.value)}
                            >

                                <option>English</option>
                                <option>Hindi</option>

                            </select>

                        </div>

                    </div>

                    {/* Right */}

                    <div className="lg:col-span-2">

                        <div className="bg-white rounded-2xl shadow p-6">

                            <label className="font-semibold">

                                Describe your content

                            </label>

                            <textarea

                                rows="8"

                                value={prompt}

                                onChange={(e)=>setPrompt(e.target.value)}

                                className="w-full mt-3 border rounded-xl p-4"

                                placeholder="Example:
Write an Instagram caption for a digital marketing agency launching an AI content tool."

                            />

                            <button

                                className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl flex items-center gap-3"

                            >

                                <Sparkles size={20}/>

                                Generate Content

                            </button>

                        </div>

                        <div className="bg-white rounded-2xl shadow p-6 mt-8">

                            <div className="flex justify-between items-center mb-5">

                                <h3 className="text-xl font-semibold">

                                    Generated Content

                                </h3>

                                <div className="flex gap-3">

                                    <button className="border rounded-lg px-4 py-2 flex items-center gap-2">

                                        <Copy size={16}/>

                                        Copy

                                    </button>

                                    <button className="border rounded-lg px-4 py-2 flex items-center gap-2">

                                        <Download size={16}/>

                                        Download

                                    </button>

                                    <button className="border rounded-lg px-4 py-2 flex items-center gap-2">

                                        <RotateCcw size={16}/>

                                        Regenerate

                                    </button>

                                </div>

                            </div>

                            <div className="min-h-[300px] bg-slate-50 rounded-xl border p-5 text-slate-500">

                                Your generated content will appear here...

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

}