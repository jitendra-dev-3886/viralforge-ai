import { useEffect, useState } from "react";
import { Flame, Lightbulb, Pencil, RefreshCw } from "lucide-react";
import { getTrending } from "../../api/trends";

export default function TrendingTopics({ niche, onSelect }) {
    const [activeTab, setActiveTab] = useState("trending");
    const [trendingTopics, setTrendingTopics] = useState([]);
    const [topicLimit, setTopicLimit] = useState(24);
    const [topicMeta, setTopicMeta] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [myTopic, setMyTopic] = useState("");

    useEffect(() => {
        setTopicLimit(24);
    }, [niche]);

    useEffect(() => {
        let cancelled = false;

        const fetchTrending = async () => {
            if (!niche) {
                setTrendingTopics([]);
                setTopicMeta(null);
                return;
            }

            setLoading(true);
            setError("");

            try {
                const data = await getTrending(niche, topicLimit);
                const topics = Array.isArray(data) ? data : data?.trends || [];
                const relevantTopics = topics
                    .map((item) => (
                        typeof item === "string"
                            ? { title: item, source: "live" }
                            : item
                    ))
                    .filter((item) => item?.title);

                if (!cancelled) {
                    setTrendingTopics(relevantTopics);
                    setTopicMeta(data && !Array.isArray(data) ? data : null);
                }
            } catch (err) {
                console.error("Trending fetch failed", err);
                if (!cancelled) {
                    setError("Unable to load niche topics right now.");
                    setTrendingTopics([]);
                    setTopicMeta(null);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        fetchTrending();

        return () => {
            cancelled = true;
        };
    }, [niche, topicLimit]);

    const displayNiche = topicMeta?.niche || niche.replaceAll("_", " ");
    const ideaTopics = trendingTopics.filter((topic) => topic.source !== "live");

    const topicCard = (topic, index, icon) => (
        <button
            type="button"
            key={`${topic.title}-${index}`}
            onClick={() => onSelect(topic.title)}
            className="w-full rounded-xl border border-slate-200 p-3 text-left text-sm text-slate-700 transition hover:border-blue-500 hover:bg-blue-50"
        >
            <div className="flex items-start justify-between gap-3">
                <span>{icon} {topic.title}</span>
                {topic.source === "live" && (
                    <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
                        Live
                    </span>
                )}
            </div>
        </button>
    );

    return (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-1 text-lg font-semibold text-slate-900">
                5. Choose a topic
            </h2>
            <p className="mb-4 text-sm text-slate-500">
                Choose from live niche trends, niche-specific content ideas, or write a custom brief.
            </p>

            <div className="mb-4 flex flex-wrap gap-2">
                <button
                    type="button"
                    onClick={() => setActiveTab("trending")}
                    className={`rounded-lg px-5 py-2 ${
                        activeTab === "trending"
                            ? "bg-blue-600 text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                >
                    <Flame size={18} className="mr-2 inline" />
                    Trending
                </button>

                <button
                    type="button"
                    onClick={() => setActiveTab("ideas")}
                    className={`rounded-lg px-5 py-2 ${
                        activeTab === "ideas"
                            ? "bg-blue-600 text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                >
                    <Lightbulb size={18} className="mr-2 inline" />
                    Niche Ideas
                </button>

                <button
                    type="button"
                    onClick={() => setActiveTab("custom")}
                    className={`rounded-lg px-5 py-2 ${
                        activeTab === "custom"
                            ? "bg-blue-600 text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                >
                    <Pencil size={18} className="mr-2 inline" />
                    My Topic
                </button>
            </div>

            {activeTab === "trending" && (
                <div>
                    {loading ? (
                        <div className="space-y-3">
                            {[1, 2, 3, 4].map((item) => (
                                <div key={item} className="h-14 animate-pulse rounded-xl bg-slate-100" />
                            ))}
                        </div>
                    ) : (
                        <>
                            {error && (
                                <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                                    {error}
                                </div>
                            )}

                            <div className="mb-4 flex flex-wrap items-center justify-between gap-2 text-sm text-slate-500">
                                <span>
                                    Showing {trendingTopics.length} topics for {displayNiche}.
                                </span>
                                {topicLimit < 30 && trendingTopics.length > 0 && (
                                    <button
                                        type="button"
                                        onClick={() => setTopicLimit(30)}
                                        className="inline-flex items-center gap-1 font-medium text-blue-600 hover:text-blue-700"
                                    >
                                        <RefreshCw size={15} />
                                        Show more
                                    </button>
                                )}
                            </div>

                            {topicMeta?.live_count === 0 && (
                                <p className="mb-4 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
                                    Live trend sources are unavailable, so these are niche-specific content ideas.
                                </p>
                            )}

                            <div className="grid max-h-[460px] gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                                {trendingTopics.map((topic, index) => topicCard(topic, index, "🔥"))}
                            </div>

                            {!trendingTopics.length && !error && (
                                <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
                                    Select a niche to load matching topic ideas.
                                </p>
                            )}
                        </>
                    )}
                </div>
            )}

            {activeTab === "ideas" && (
                <div className="grid max-h-[460px] gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                    {(ideaTopics.length ? ideaTopics : trendingTopics).map((topic, index) => (
                        topicCard(topic, index, "💡")
                    ))}
                    {!trendingTopics.length && (
                        <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600 md:col-span-2">
                            Select a niche first to load matching ideas.
                        </p>
                    )}
                </div>
            )}

            {activeTab === "custom" && (
                <textarea
                    rows={5}
                    placeholder="Write your own topic..."
                    value={myTopic}
                    onChange={(event) => {
                        setMyTopic(event.target.value);
                        onSelect(event.target.value);
                    }}
                    className="w-full rounded-xl border p-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            )}
        </section>
    );
}
