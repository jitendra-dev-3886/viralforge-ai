import { useEffect, useState } from "react";
import { Flame, Pencil } from "lucide-react";
import { getTrending } from "../../api/trends";

export default function TrendingTopics({ niche, projectId, platform, contentType, onSelect, value, title = "5. Choose a topic" }) {
    const [activeTab, setActiveTab] = useState("trending");
    const [trendingTopics, setTrendingTopics] = useState([]);
    const [topicMeta, setTopicMeta] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [myTopic, setMyTopic] = useState("");

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
                const data = await getTrending(niche, 10, { project_id: projectId || undefined, platform, content_type: contentType });
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
                    const detail = err.response?.data?.detail;
                    setError(typeof detail === "string" ? detail : detail?.message || "Unable to load creator topics right now.");
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
    }, [niche, projectId, platform, contentType]);

    const displayNiche = topicMeta?.niche || (niche || "").replaceAll("_", " ");

    const topicCard = (topic, index, icon) => (
        <button
            type="button"
            key={`${topic.title}-${index}`}
            onClick={() => onSelect(topic.title)}
            aria-pressed={value === undefined ? undefined : value === topic.title}
            className="w-full rounded-xl border border-slate-200 p-3 text-left text-sm text-slate-700 transition hover:border-blue-500 hover:bg-blue-50"
        >
            <div className="flex items-start justify-between gap-3">
                <span><span className="mb-1 block text-xs text-slate-500">{topic.language === "hi" ? "हिंदी" : "English"}</span>{icon} {topic.title}</span>
                    <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
                        Trend-based
                    </span>
            </div>
            {topic.source_title && <p className="mt-2 text-xs text-slate-500">Based on: {topic.source_title}</p>}
        </button>
    );

    return (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-1 text-lg font-semibold text-slate-900">
                {title}
            </h2>
            <p className="mb-4 text-sm text-slate-500">
                Up to 5 Hindi and 5 English creator-ready topics, based on recent trends and filtered for your niche and audience.
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
                    Creator trends
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

                            </div>

                            {trendingTopics.length > 0 && trendingTopics.length < 10 && (
                                <p className="mb-4 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
                                    Fewer than 5 live topics are currently available in one or both languages. Only available results are shown.
                                </p>
                            )}

                            <div className="grid max-h-[460px] gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                                {trendingTopics.map((topic, index) => topicCard(topic, index, "🔥"))}
                            </div>

                            {!trendingTopics.length && !error && (
                                <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
                                    {niche ? "No live topics are available right now. Try again later or enter your own topic." : "Select a niche to load live topics."}
                                </p>
                            )}
                        </>
                    )}
                </div>
            )}

            {activeTab === "custom" && (
                <textarea
                    rows={5}
                    placeholder="Write your own topic..."
                    value={value ?? myTopic}
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
