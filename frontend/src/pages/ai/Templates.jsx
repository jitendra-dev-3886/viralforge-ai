import { useNavigate } from "react-router-dom";
import templates from "../../data/templates";

export default function Templates() {

    const navigate = useNavigate();

    return (

        <div className="min-h-screen bg-slate-100 p-4 sm:p-6 lg:p-10">

            <div className="mb-10">

                <h1 className="text-4xl font-bold">
                    AI Templates
                </h1>

                <p className="text-slate-500 mt-2">
                    Choose what you want AI to create.
                </p>

            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">

                {templates.map((template) => (

                    <div
                        key={template.id}
                        className="cursor-pointer rounded-2xl bg-white p-5 shadow transition hover:shadow-xl sm:p-8"
                        onClick={() =>
                            navigate(
                                `/generator/${template.id}`
                            )
                        }
                    >

                        <div className="text-5xl">
                            {template.icon}
                        </div>

                        <h2 className="text-2xl font-bold mt-6">
                            {template.title}
                        </h2>

                        <p className="text-slate-500 mt-3">
                            {template.description}
                        </p>

                        <button
                            className="mt-8 bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-5 py-3"
                        >
                            Use Template
                        </button>

                    </div>

                ))}

            </div>

        </div>

    );

}
