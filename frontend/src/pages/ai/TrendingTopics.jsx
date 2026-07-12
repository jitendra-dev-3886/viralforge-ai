import { useState } from "react";
import { Flame, Lightbulb, Pencil } from "lucide-react";

export default function TrendingTopics({ onSelect }) {

    const [activeTab, setActiveTab] = useState("trending");

    const trendingTopics = [
        "Krishna's Biggest Life Lesson",
        "Power of Karma",
        "Morning Meditation Benefits",
        "Passive Income in 2026",
        "Why People Overthink",
        "Universe Hidden Secrets",
    ];

    const aiIdeas = [
        "If Krishna Lived Today...",
        "5 Habits of Rich People",
        "The Secret Behind Black Holes",
        "Why Smart People Stay Silent",
        "Signs of True Love",
        "Power of Positive Thinking",
    ];

    const [myTopic, setMyTopic] = useState("");

    return (

        <div className="mt-10 bg-white rounded-2xl shadow p-6">

            <h2 className="text-2xl font-bold mb-6">
                Choose Topic
            </h2>

            {/* Tabs */}

            <div className="flex gap-3 mb-6">

                <button
                    onClick={() => setActiveTab("trending")}
                    className={`px-5 py-2 rounded-lg ${
                        activeTab === "trending"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100"
                    }`}
                >
                    <Flame size={18} className="inline mr-2" />
                    Trending
                </button>

                <button
                    onClick={() => setActiveTab("ideas")}
                    className={`px-5 py-2 rounded-lg ${
                        activeTab === "ideas"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100"
                    }`}
                >
                    <Lightbulb size={18} className="inline mr-2" />
                    AI Ideas
                </button>

                <button
                    onClick={() => setActiveTab("custom")}
                    className={`px-5 py-2 rounded-lg ${
                        activeTab === "custom"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100"
                    }`}
                >
                    <Pencil size={18} className="inline mr-2" />
                    My Topic
                </button>

            </div>

            {/* Trending */}

            {activeTab === "trending" && (

                <div className="grid md:grid-cols-2 gap-4">

                    {trendingTopics.map((topic) => (

                        <div
                            key={topic}
                            onClick={() => onSelect(topic)}
                            className="cursor-pointer border rounded-xl p-4 hover:border-blue-600 hover:bg-blue-50"
                        >
                            🔥 {topic}
                        </div>

                    ))}

                </div>

            )}

            {/* AI Ideas */}

            {activeTab === "ideas" && (

                <div className="grid md:grid-cols-2 gap-4">

                    {aiIdeas.map((topic) => (

                        <div
                            key={topic}
                            onClick={() => onSelect(topic)}
                            className="cursor-pointer border rounded-xl p-4 hover:border-green-600 hover:bg-green-50"
                        >
                            💡 {topic}
                        </div>

                    ))}

                </div>

            )}

            {/* Custom Topic */}

            {activeTab === "custom" && (

                <div>

                    <textarea
                        rows={5}
                        placeholder="Write your own topic..."
                        value={myTopic}
                        onChange={(e) => {
                            setMyTopic(e.target.value);
                            onSelect(e.target.value);
                        }}
                        className="w-full border rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                </div>

            )}

        </div>

    );

}