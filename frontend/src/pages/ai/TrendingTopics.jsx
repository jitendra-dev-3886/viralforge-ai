import { useEffect, useState } from "react";
import { Flame, Lightbulb, Pencil } from "lucide-react";
import { getTrending } from "../../api/trends";

const defaultTrendingTopics = [
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

const nicheCategoryMap = {
    morning_spiritual: "Spiritual",
    financial_freedom: "Finance",
    cosmic_knowledge: "Spiritual",
    psychology: "Psychology",
    love_romantic: "Entertainment",
};

export default function TrendingTopics({ niche, onSelect }) {

    const [activeTab, setActiveTab] = useState("trending");
    const [trendingTopics, setTrendingTopics] = useState(defaultTrendingTopics);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [myTopic, setMyTopic] = useState("");

    useEffect(() => {
        const fetchTrending = async () => {
            if (!niche) {
                setTrendingTopics(defaultTrendingTopics);
                return;
            }

            setLoading(true);
            setError("");

            try {
                const data = await getTrending(niche);
                const topics = Array.isArray(data) ? data : data?.trends || [];
                const category = nicheCategoryMap[niche];

                const filtered = topics
                    .filter((item) => {
                        if (!item || typeof item !== "object") return false;
                        if (category && item.category) {
                            return item.category.toLowerCase() === category.toLowerCase();
                        }
                        return true;
                    })
                    .map((item) => item.title)
                    .filter(Boolean);

                setTrendingTopics(filtered.length > 0 ? filtered : defaultTrendingTopics);
            } catch (err) {
                console.error("Trending fetch failed", err);
                setError("Unable to load trending topics right now.");
                setTrendingTopics(defaultTrendingTopics);
            } finally {
                setLoading(false);
            }
        };

        fetchTrending();
    }, [niche]);

    return (

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

            <h2 className="mb-1 text-lg font-semibold text-slate-900">
                5. Choose a topic
            </h2>
            <p className="mb-4 text-sm text-slate-500">Use a trend, a suggested idea, or write a custom brief.</p>

            {/* Tabs */}

            <div className="mb-4 flex flex-wrap gap-2">

                <button
                    onClick={() => setActiveTab("trending")}
                    className={`px-5 py-2 rounded-lg ${
                        activeTab === "trending"
                            ? "bg-blue-600 text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
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
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
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
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                >
                    <Pencil size={18} className="inline mr-2" />
                    My Topic
                </button>

            </div>

            {/* Trending */}

            {activeTab === "trending" && (

                <div>
                    {loading ? (
                        <div className="space-y-3">
                            {[1, 2, 3].map((item) => (
                                <div key={item} className="h-14 rounded-xl bg-slate-100 animate-pulse" />
                            ))}
                        </div>
                    ) : (
                        <>
                            {error && (
                                <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                                    {error}
                                </div>
                            )}

                            <div className="mb-4 text-sm text-slate-500">
                                Showing {trendingTopics.length} trending topics.
                            </div>
                            <div className="grid gap-2 md:grid-cols-2 max-h-[320px] overflow-y-auto pr-1">
                                {trendingTopics.map((topic) => (
                                    <div
                                        key={topic}
                                        onClick={() => onSelect(topic)}
                                        className="cursor-pointer rounded-xl border border-slate-200 p-3 text-sm text-slate-700 transition hover:border-blue-500 hover:bg-blue-50"
                                    >
                                        🔥 {topic}
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </div>

            )}

            {/* AI Ideas */}

            {activeTab === "ideas" && (

                <div className="grid gap-2 md:grid-cols-2">

                    {aiIdeas.map((topic) => (

                        <div
                            key={topic}
                            onClick={() => onSelect(topic)}
                            className="cursor-pointer rounded-xl border border-slate-200 p-3 text-sm text-slate-700 transition hover:border-blue-500 hover:bg-blue-50"
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

        </section>

    );

}
