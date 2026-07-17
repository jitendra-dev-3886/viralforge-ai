export default function SummaryPanel({
    platforms,
    contents,
    niche,
    topic,
    packageType,
}) {

    return (

        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl shadow-xl p-8 mt-8 text-white">

            <h2 className="text-2xl font-bold">
                🚀 Generation Summary
            </h2>

            <p className="mt-2 text-indigo-100">
                Review everything before generating AI content.
            </p>

            <div className="grid md:grid-cols-2 gap-8 mt-8">

                <div>

                    <h3 className="font-semibold mb-3">
                        Platforms
                    </h3>

                    {
                        platforms.length
                            ? platforms.map((item) => (
                                <div key={item}>
                                    ✅ {item}
                                </div>
                            ))
                            : <div className="text-indigo-200">No platform selected</div>
                    }

                </div>

                <div>

                    <h3 className="font-semibold mb-3">
                        Content Types
                    </h3>

                    {
                        contents.length
                            ? contents.map((item) => (
                                <div key={item}>
                                    🎬 {item}
                                </div>
                            ))
                            : <div className="text-indigo-200">No content selected</div>
                    }

                </div>

                <div>

                    <h3 className="font-semibold mb-3">
                        Niche
                    </h3>

                    <div>
                        {niche || "-"}
                    </div>

                </div>

                <div>

                    <h3 className="font-semibold mb-3">
                        Topic
                    </h3>

                    <div>
                        {topic || "-"}
                    </div>

                </div>

                <div>

                    <h3 className="font-semibold mb-3">
                        Package
                    </h3>

                    <div>
                        {packageType}
                    </div>

                </div>

                <div>

                    <h3 className="font-semibold mb-3">
                        Estimated Output
                    </h3>

                    <div>
                        {contents.length} Content
                    </div>

                </div>

            </div>

        </div>

    );

}