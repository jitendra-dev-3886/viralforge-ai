const niches = [
    {
        id: "morning_spiritual",
        title: "Morning Spiritual",
        shortTitle: "Spiritual",
        icon: "🌅",
        description: "Mindfulness, wisdom & inner peace",
        color: "amber",
    },
    {
        id: "financial_freedom",
        title: "Financial Freedom",
        shortTitle: "Finance",
        icon: "💰",
        description: "Money, investing & wealth mindset",
        color: "emerald",
    },
    {
        id: "cosmic_knowledge",
        title: "Cosmic Knowledge",
        shortTitle: "Cosmos",
        icon: "🌌",
        description: "Space, universe & cosmic mysteries",
        color: "indigo",
    },
    {
        id: "psychology",
        title: "Psychology",
        shortTitle: "Psychology",
        icon: "🧠",
        description: "Human behavior & mind",
        color: "violet",
    },
    {
        id: "love_romantic",
        title: "Love & Romance",
        shortTitle: "Relationships",
        icon: "❤️",
        description: "Love, attraction & relationships",
        color: "rose",
    },
    {
        id: "ai_technology",
        title: "AI & Technology",
        shortTitle: "AI & Tech",
        icon: "🤖",
        description: "AI, coding, web & future tech",
        color: "blue",
    },
];

const colorClasses = {
    amber: {
        active: "border-amber-500 bg-amber-50 ring-2 ring-amber-100",
        hover: "hover:border-amber-300",
        icon: "bg-amber-100",
    },
    emerald: {
        active: "border-emerald-500 bg-emerald-50 ring-2 ring-emerald-100",
        hover: "hover:border-emerald-300",
        icon: "bg-emerald-100",
    },
    indigo: {
        active: "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-100",
        hover: "hover:border-indigo-300",
        icon: "bg-indigo-100",
    },
    violet: {
        active: "border-violet-500 bg-violet-50 ring-2 ring-violet-100",
        hover: "hover:border-violet-300",
        icon: "bg-violet-100",
    },
    rose: {
        active: "border-rose-500 bg-rose-50 ring-2 ring-rose-100",
        hover: "hover:border-rose-300",
        icon: "bg-rose-100",
    },
    blue: {
        active: "border-blue-500 bg-blue-50 ring-2 ring-blue-100",
        hover: "hover:border-blue-300",
        icon: "bg-blue-100",
    },
};

export default function NicheSelector({
    selected,
    onChange,
}) {
    return (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

            {/* Header */}
            <div className="mb-5 flex items-start justify-between gap-4">

                <div>
                    <div className="flex items-center gap-2">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
                            3
                        </span>

                        <h2 className="text-lg font-semibold text-slate-900">
                            Choose a niche
                        </h2>
                    </div>

                    <p className="mt-1 ml-9 text-sm text-slate-500">
                        Select the content niche for your AI-generated content.
                    </p>
                </div>

                {selected && (
                    <div className="hidden rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 sm:block">
                        {niches.find((niche) => niche.id === selected)?.shortTitle}
                    </div>
                )}

            </div>

            {/* Niche Grid */}
            <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">

                {niches.map((niche) => {
                    const isSelected = selected === niche.id;
                    const colors = colorClasses[niche.color];

                    return (
                        <button
                            type="button"
                            key={niche.id}
                            onClick={() => onChange(niche.id)}
                            aria-pressed={isSelected}
                            aria-label={`Select ${niche.title} niche`}
                            className={`
                                group relative rounded-2xl border p-4
                                text-center
                                transition-all duration-200
                                focus:outline-none
                                focus-visible:ring-2
                                focus-visible:ring-blue-500
                                focus-visible:ring-offset-2

                                ${
                                    isSelected
                                        ? colors.active
                                        : `border-slate-200 bg-white ${colors.hover} hover:-translate-y-0.5 hover:shadow-md`
                                }
                            `}
                        >

                            {/* Selected Indicator */}
                            {isSelected && (
                                <span className="absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
                                    ✓
                                </span>
                            )}

                            {/* Icon */}
                            <div
                                className={`
                                    mx-auto flex h-14 w-14
                                    items-center justify-center
                                    rounded-2xl text-3xl
                                    transition-transform duration-200
                                    ${
                                        isSelected
                                            ? colors.icon
                                            : "bg-slate-50 group-hover:scale-110"
                                    }
                                `}
                            >
                                {niche.icon}
                            </div>

                            {/* Title */}
                            <h3 className="mt-3 text-sm font-semibold text-slate-800">
                                {niche.title}
                            </h3>

                            {/* Description */}
                            <p className="mt-1 text-[11px] leading-4 text-slate-500">
                                {niche.description}
                            </p>

                        </button>
                    );
                })}

            </div>

            {/* Selected Niche */}
            {selected && (
                <div className="mt-4 flex items-center gap-2 rounded-xl border border-blue-100 bg-blue-50 px-4 py-3">

                    <span className="text-lg">
                        {niches.find((niche) => niche.id === selected)?.icon}
                    </span>

                    <div className="min-w-0">
                        <p className="text-xs font-medium text-blue-600">
                            Selected niche
                        </p>

                        <p className="truncate text-sm font-semibold text-slate-800">
                            {niches.find((niche) => niche.id === selected)?.title}
                        </p>
                    </div>

                </div>
            )}

        </section>
    );
}