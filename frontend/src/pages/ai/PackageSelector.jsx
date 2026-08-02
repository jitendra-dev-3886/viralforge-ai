import {
    Quote,
    Clapperboard,
    Images,
    BookOpen,
    Package,
} from "lucide-react";

const packages = [

    {
        id: "quote",
        title: "Quote",
        description: "Motivational Quote + Caption",
        icon: Quote,
    },

    {
        id: "reel",
        title: "Reel",
        description: "30-60 sec Viral Reel",
        icon: Clapperboard,
    },

    {
        id: "carousel",
        title: "Carousel",
        description: "8-10 Story Slides",
        icon: Images,
    },

    {
        id: "story",
        title: "Short Story",
        description: "Story with Hook & Ending",
        icon: BookOpen,
    },

    {
        id: "complete",
        title: "Complete Package",
        description: "Everything Included",
        icon: Package,
    },

];

export default function PackageSelector({

    selected,
    onChange,

}) {

    return (

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

            <h2 className="mb-1 text-lg font-semibold text-slate-900">
                4. Choose a package
            </h2>
            <p className="mb-4 text-sm text-slate-500">Choose the depth and output style for this generation.</p>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">

                {packages.map((item) => {

                    const Icon = item.icon;

                    return (

                        <button
                            type="button"
                            key={item.id}
                            onClick={() => onChange(item.id)}
                            className={`rounded-xl border p-4 text-left transition duration-200

                            ${
                                selected === item.id
                                    ? "border-blue-600 bg-blue-50 shadow-sm"
                                    : "border-slate-200 bg-white hover:border-blue-400"
                            }`}
                        >

                            <Icon
                                size={26}
                                className="text-blue-600"
                            />

                            <h3 className="mt-3 text-sm font-semibold text-slate-900">

                                {item.title}

                            </h3>

                            <p className="mt-1 text-xs text-slate-500">

                                {item.description}

                            </p>

                        </button>

                    );

                })}

            </div>

        </section>

    );

}
