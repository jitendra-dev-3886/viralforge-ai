const niches = [
    {
        id: "morning_spiritual",
        title: "Morning Spiritual",
        icon: "🌅",
    },
    {
        id: "financial_freedom",
        title: "Financial Freedom",
        icon: "💰",
    },
    {
        id: "cosmic_knowledge",
        title: "Cosmic Knowledge",
        icon: "🌌",
    },
    {
        id: "psychology",
        title: "Psychology",
        icon: "🧠",
    },
    {
        id: "love_romantic",
        title: "Love & Romantic",
        icon: "❤️",
    },
];

export default function NicheSelector({
    selected,
    onChange,
}) {
    return (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

            <h2 className="mb-1 text-lg font-semibold text-slate-900">
                3. Choose a niche
            </h2>
            <p className="mb-4 text-sm text-slate-500">This guides the voice, hooks, and examples used in the output.</p>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">

                {niches.map((niche) => (

                    <button
                        type="button"
                        key={niche.id}
                        onClick={() => onChange(niche.id)}
                        className={`rounded-xl border p-4 text-center transition-all duration-200
                        ${
                            selected === niche.id
                                ? "border-blue-600 bg-blue-50 shadow-sm"
                                : "border-slate-200 bg-white hover:border-blue-400"
                        }`}
                    >

                        <div className="text-3xl">
                            {niche.icon}
                        </div>

                        <h3 className="mt-2 text-sm font-medium text-slate-800">
                            {niche.title}
                        </h3>

                    </button>

                ))}

            </div>

        </section>
    );
}
