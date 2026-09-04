import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProject } from "../../api/project";

export default function ProjectDetail() {
    const { id } = useParams();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadProject = async () => {
            try {
                const response = await getProject(id);
                setProject(response.project || response);
            } catch (err) {
                console.error(err);
                setError("Unable to load project.");
            } finally {
                setLoading(false);
            }
        };

        loadProject();
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 text-slate-500">
                Loading project...
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 text-red-600">
                {error}
            </div>
        );
    }

    if (!project) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 text-slate-500">
                Project not found.
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-3xl p-1 sm:p-4 lg:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">{project.title}</h1>
                    <p className="text-slate-500 mt-2">{project.topic}</p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <Link to="/projects" className="rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                        Back to projects
                    </Link>
                    <Link to={`/projects/${project.id}/edit`} className="rounded-2xl bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
                        Edit Project
                    </Link>
                </div>
            </div>

            <div className="grid gap-6">
                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                    <h2 className="text-xl font-semibold mb-4">Project details</h2>
                    <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                            <p className="text-sm text-slate-500">Topic</p>
                            <p className="mt-2 text-slate-900">{project.topic}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Platform</p>
                            <p className="mt-2 text-slate-900">{project.platform}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Content Type</p>
                            <p className="mt-2 text-slate-900">{project.content_type}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Status</p>
                            <p className="mt-2 text-slate-900">{project.status || "draft"}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Language</p>
                            <p className="mt-2 text-slate-900">{project.language || "English"}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Brand ID</p>
                            <p className="mt-2 text-slate-900">{project.brand_id ?? "None"}</p>
                        </div>
                    </div>
                </div>

                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                    <h2 className="text-xl font-semibold mb-4">AI settings</h2>
                    <div className="grid gap-4">
                        <div>
                            <p className="text-sm text-slate-500">Provider</p>
                            <p className="mt-2 text-slate-900">{project.ai_provider || "None"}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Prompt</p>
                            <p className="mt-2 text-slate-900 whitespace-pre-wrap">{project.prompt || "No prompt set."}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
