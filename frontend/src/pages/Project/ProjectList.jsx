import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useProject } from "../../context/ProjectContext";

export default function ProjectList() {
    const { projects, loading, loadProjects, removeProject } = useProject();

    useEffect(() => {
        loadProjects();
    }, []);

    const handleDelete = async (projectId) => {
        if (window.confirm("Delete this project? This cannot be undone.")) {
            await removeProject(projectId);
        }
    };

    return (
        <div className="p-8">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Projects</h1>
                    <p className="text-slate-500 mt-2">Browse and manage your AI content projects.</p>
                </div>
                <Link
                    to="/projects/create"
                    className="inline-flex items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-white hover:bg-blue-700 transition"
                >
                    + New Project
                </Link>
            </div>

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((item) => (
                        <div key={item} className="animate-pulse rounded-2xl border bg-white p-6 h-40" />
                    ))}
                </div>
            ) : projects.length === 0 ? (
                <div className="rounded-2xl border border-dashed p-16 text-center bg-white">
                    <h2 className="text-2xl font-semibold">No projects yet</h2>
                    <p className="text-slate-500 mt-2">Create a project to start generating content from your brands and prompts.</p>
                </div>
            ) : (
                <div className="grid gap-6">
                    {projects.map((project) => (
                        <div key={project.id} className="rounded-3xl border bg-white p-6 shadow-sm">
                            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                                <div>
                                    <h2 className="text-xl font-semibold text-slate-900">{project.title}</h2>
                                    <p className="mt-2 text-slate-500">{project.topic}</p>
                                </div>
                                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs uppercase tracking-wide text-slate-600">
                                    {project.status || "draft"}
                                </span>
                            </div>

                            <div className="mt-5 grid gap-3 sm:grid-cols-3 text-sm text-slate-600">
                                <div>
                                    <span className="font-medium">Platform:</span> {project.platform}
                                </div>
                                <div>
                                    <span className="font-medium">Content Type:</span> {project.content_type}
                                </div>
                                <div>
                                    <span className="font-medium">Language:</span> {project.language || "English"}
                                </div>
                            </div>

                            <div className="mt-6 flex flex-wrap gap-3">
                                <Link
                                    to={`/projects/${project.id}`}
                                    className="rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                >
                                    View
                                </Link>
                                <Link
                                    to={`/projects/${project.id}/edit`}
                                    className="rounded-2xl border border-blue-600 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
                                >
                                    Edit
                                </Link>
                                <button
                                    onClick={() => handleDelete(project.id)}
                                    className="rounded-2xl border border-red-200 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
