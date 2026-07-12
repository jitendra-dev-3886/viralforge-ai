import { Sparkles, Loader2 } from "lucide-react";

export default function GenerateButton({

    onGenerate,

    loading,

}) {

    return (

        <div className="mt-10 text-center">

            <button

                onClick={onGenerate}

                disabled={loading}

                className="bg-gradient-to-r from-blue-600 to-indigo-600
                hover:from-blue-700 hover:to-indigo-700
                text-white
                px-12
                py-4
                rounded-2xl
                text-lg
                font-semibold
                shadow-lg
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

                AI will generate platform-specific content for
                Instagram, Facebook & YouTube.

            </p>

        </div>

    );

}