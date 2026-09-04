import { useParams } from "react-router-dom";
import templates from "../../data/templates";
import { useState } from "react";

export default function AIGenerator() {

    const { template } = useParams();

    const currentTemplate = templates.find(
        item => item.id === template
    );

    const [prompt, setPrompt] = useState("");

    const [result, setResult] = useState("");

    const [loading, setLoading] = useState(false);

    const handleGenerate = () => {

        setLoading(true);

        // Backend integration later

        setTimeout(() => {

            setResult(
                "AI response will appear here..."
            );

            setLoading(false);

        },1000);

    };

    if(!currentTemplate){

        return(

            <div className="p-10">

                Template Not Found

            </div>

        );

    }

    return (

        <div className="min-h-screen bg-slate-100">

            <div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-10">

                <div>

                    <div className="text-6xl">

                        {currentTemplate.icon}

                    </div>

                    <h1 className="text-4xl font-bold mt-5">

                        {currentTemplate.title}

                    </h1>

                    <p className="text-slate-500 mt-3">

                        {currentTemplate.description}

                    </p>

                </div>

                <div className="grid lg:grid-cols-2 gap-8 mt-10">

                    {/* LEFT */}

                    <div className="rounded-2xl bg-white p-4 shadow sm:p-8">

                        <h2 className="text-xl font-bold">

                            Prompt

                        </h2>

                        <textarea

                            rows={12}

                            value={prompt}

                            onChange={(e)=>
                                setPrompt(e.target.value)
                            }

                            className="w-full border rounded-xl p-4 mt-5"

                            placeholder="Describe what you want AI to generate..."

                        />

                        <button

                            onClick={handleGenerate}

                            className="mt-6 bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-6 py-3"

                        >

                            {

                                loading

                                ?

                                "Generating..."

                                :

                                "Generate"

                            }

                        </button>

                    </div>

                    {/* RIGHT */}

                    <div className="rounded-2xl bg-white p-4 shadow sm:p-8">

                        <div className="flex justify-between">

                            <h2 className="text-xl font-bold">

                                AI Output

                            </h2>

                        </div>

                        <div className="mt-5 border rounded-xl min-h-[400px] p-5 whitespace-pre-wrap">

                            {

                                result ||

                                "Generated content will appear here."

                            }

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

}
