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

        <div className="mt-10">

            <h2 className="text-2xl font-bold mb-5">
                Select Content Package
            </h2>

            <div className="grid md:grid-cols-2 xl:grid-cols-5 gap-5">

                {packages.map((item) => {

                    const Icon = item.icon;

                    return (

                        <div
                            key={item.id}
                            onClick={() => onChange(item.id)}
                            className={`cursor-pointer rounded-2xl border-2 p-6 transition duration-300

                            ${
                                selected === item.id
                                    ? "border-blue-600 bg-blue-50 shadow-lg"
                                    : "border-gray-200 bg-white hover:border-blue-400 hover:shadow"
                            }`}
                        >

                            <Icon
                                size={38}
                                className="text-blue-600"
                            />

                            <h3 className="mt-4 text-lg font-bold">

                                {item.title}

                            </h3>

                            <p className="text-gray-500 text-sm mt-2">

                                {item.description}

                            </p>

                        </div>

                    );

                })}

            </div>

        </div>

    );

}