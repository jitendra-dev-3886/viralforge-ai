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
        <div className="mt-8">

            <h2 className="text-2xl font-bold mb-5">
                Select Niche
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-5">

                {niches.map((niche) => (

                    <div
                        key={niche.id}
                        onClick={() => onChange(niche.id)}
                        className={`cursor-pointer rounded-2xl border-2 p-6 transition-all duration-300 text-center
                        ${
                            selected === niche.id
                                ? "border-blue-600 bg-blue-50 shadow-lg"
                                : "border-gray-200 bg-white hover:border-blue-400 hover:shadow"
                        }`}
                    >

                        <div className="text-5xl">
                            {niche.icon}
                        </div>

                        <h3 className="mt-4 text-lg font-semibold">
                            {niche.title}
                        </h3>

                    </div>

                ))}

            </div>

        </div>
    );
}