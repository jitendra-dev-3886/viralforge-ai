import { Sparkles, Loader2 } from "lucide-react";

export default function GenerateButton({

    onGenerate,

    loading,

    disabled = false,

}) {

    return (

        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-sm">

            <button

                onClick={onGenerate}

                disabled={loading || disabled}

                className="bg-gradient-to-r from-blue-600 to-indigo-600
                hover:from-blue-700 hover:to-indigo-700
                text-white
                px-8
                py-3
                rounded-xl
                text-base
                font-semibold
                shadow-sm
                transition-all
                disabled:opacity-60
                disabled:cursor-not-allowed
                flex
                items-center
                justify-center
                gap-3
                mx-auto"

            >

                {

                    loading ?

                    <>

                        <Loader2
                            size={22}
                            className="animate-spin"
                        />

                        Generating AI Content...

                    </>

                    :

                    <>

                        <Sparkles size={22} />

                        Generate AI Content

                    </>

                }

            </button>

            <p className="text-gray-500 text-sm mt-3">

                {disabled && !loading
                    ? "Complete the required selections above to generate content."
                    : "AI will generate platform-specific content for your selected channels."}

            </p>

        </div>

    );

}
