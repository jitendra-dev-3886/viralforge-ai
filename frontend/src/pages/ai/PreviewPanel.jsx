import {
    Sparkles,
    Copy,
} from "lucide-react";


export default function PreviewPanel({ data }) {


    if (!data || !data.data) {

        return (

            <div className="mt-10 bg-white rounded-2xl shadow-lg p-10 text-center">

                <Sparkles
                    size={70}
                    className="mx-auto text-blue-500"
                />

                <h2 className="text-3xl font-bold mt-6">
                    AI Content Preview
                </h2>

                <p className="text-gray-500 mt-4">
                    Generate content to preview results.
                </p>

            </div>

        );

    }


    const copyContent = (content) => {

        const text = `
Video:
${content.video}


Voiceover:
${content.voiceover}


Caption:
${content.caption}


Hashtags:
${content.hashtags}
        `;

        navigator.clipboard.writeText(text);

    };


    return (

        <div className="space-y-8 mt-8">


            {Object.entries(data.data).map(([platform, platformData]) => (


                <div
                    key={platform}
                    className="bg-white rounded-3xl shadow-lg p-8"
                >


                    <h2 className="text-3xl font-bold capitalize text-indigo-600 mb-8">

                        {platform.replace("_", " ")}

                    </h2>



                    {Object.entries(platformData).map(([type, content]) => (


                        <div
                            key={type}
                            className="border rounded-2xl p-6 mb-6 bg-slate-50"
                        >


                            <h3 className="text-xl font-bold capitalize mb-6">

                                {type}

                            </h3>



                            <div className="space-y-5">


                                <div>

                                    <strong>
                                        Video
                                    </strong>

                                    <p className="mt-2 text-gray-700">
                                        {content.video}
                                    </p>

                                </div>



                                <div>

                                    <strong>
                                        Voiceover
                                    </strong>

                                    <p className="mt-2 text-gray-700">
                                        {content.voiceover}
                                    </p>

                                </div>




                                <div>

                                    <strong>
                                        Caption
                                    </strong>

                                    <p className="mt-2 text-gray-700">
                                        {content.caption}
                                    </p>

                                </div>





                                <div>

                                    <strong>
                                        Hashtags
                                    </strong>


                                    <div className="flex flex-wrap gap-2 mt-3">


                                        {content.hashtags
                                            ?.split(" ")
                                            .map((tag, index) => (


                                                <span
                                                    key={index}
                                                    className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm"
                                                >

                                                    {tag}

                                                </span>


                                            ))}


                                    </div>


                                </div>



                            </div>




                            <button

                                onClick={() => copyContent(content)}

                                className="mt-8 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl flex items-center gap-2"

                            >

                                <Copy size={18} />

                                Copy Content

                            </button>



                        </div>


                    ))}



                </div>


            ))}



        </div>

    );

}