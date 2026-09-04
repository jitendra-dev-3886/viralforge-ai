import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useProject } from "../../context/ProjectContext";
import { useBrand } from "../../context/BrandContext";

const defaultForm = {
    title: "",
    topic: "",
    platform: "",
    content_type: "",
    niche: "",
    category: "",
    language: "English",
    brand_id: "",
    ai_provider: "",
    prompt: "",
};

export default function ProjectCreate() {
    const navigate = useNavigate();
    const { addProject } = useProject();
    const { brands } = useBrand();

    const [formData, setFormData] = useState(defaultForm);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const payload = {
                ...formData,
                brand_id: formData.brand_id ? Number(formData.brand_id) : null,
            };

            const response = await addProject(payload);

            if (response?.success) {
                navigate("/projects");
            } else {
                setError(response?.message || "Unable to create project.");
            }
        } catch (err) {
            console.error(err);
            setError("An unexpected error occurred. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mx-auto max-w-3xl p-1 sm:p-4 lg:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Create Project</h1>
                    <p className="text-slate-500 mt-2">Use your brand and AI settings to create a new content project.</p>
                </div>
                <Link to="/projects" className="text-sm text-slate-600 hover:text-slate-900">
                    &larr; Back to projects
                </Link>
            </div>

            {error && (
                <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6 rounded-3xl border bg-white p-4 shadow-sm sm:p-8">
                <div className="grid gap-6 md:grid-cols-2">
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Project Title *
                        <input
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            required
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Topic *
                        <input
                            name="topic"
                            value={formData.topic}
                            onChange={handleChange}
                            required
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Platform *
                        <input
                            name="platform"
                            value={formData.platform}
                            onChange={handleChange}
                            required
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                            placeholder="e.g. YouTube"
                        />
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Content Type *
                        <input
                            name="content_type"
                            value={formData.content_type}
                            onChange={handleChange}
                            required
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                            placeholder="e.g. Video"
                        />
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Language
                        <input
                            name="language"
                            value={formData.language}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Brand
                        <select
                            name="brand_id"
                            value={formData.brand_id}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        >
                            <option value="">No brand</option>
                            {brands.map((brand) => (
                                <option key={brand.id} value={brand.id}>
                                    {brand.name}
                                </option>
                            ))}
                        </select>
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Niche
                        <input
                            name="niche"
                            value={formData.niche}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Category
                        <input
                            name="category"
                            value={formData.category}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        AI Provider
                        <input
                            name="ai_provider"
                            value={formData.ai_provider}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                            placeholder="e.g. OpenAI"
                        />
                    </label>
                    <label className="space-y-2 text-sm font-medium text-slate-700">
                        Prompt
                        <input
                            name="prompt"
                            value={formData.prompt}
                            onChange={handleChange}
                            className="w-full rounded-2xl border px-4 py-3 text-slate-900"
                        />
                    </label>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center justify-center rounded-2xl bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? "Saving..." : "Create Project"}
                </button>
            </form>
        </div>
    );
}
