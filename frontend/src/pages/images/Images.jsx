import { useEffect, useState } from "react";
import { getProjects } from "../../api/project";
import { getProjectMedia } from "../../api/media";

export default function ImagesPage() {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [mediaItems, setMediaItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadProjects = async () => {
            try {
                const { projects: loadedProjects } = await getProjects();
                setProjects(loadedProjects || []);
                if (loadedProjects.length > 0) {
                    setSelectedProjectId(loadedProjects[0].id);
                }
            } catch (err) {
                console.error(err);
                setError("Unable to load projects.");
            }
        };

        loadProjects();
    }, []);

    useEffect(() => {
        if (!selectedProjectId) {
            setMediaItems([]);
            return;
        }

        const loadMedia = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await getProjectMedia(selectedProjectId);
                setMediaItems(response.media || []);
            } catch (err) {
                console.error(err);
                setError("Unable to load media for selected project.");
            } finally {
                setLoading(false);
            }
        };

        loadMedia();
    }, [selectedProjectId]);

    return (
        <div className="p-1 sm:p-4 lg:p-8">
            <h1 className="text-3xl font-bold mb-6">Image Library</h1>

            <div className="mb-6 max-w-2xl">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                    Project
                </label>
                <select
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                    value={selectedProjectId || ""}
                    onChange={(event) => setSelectedProjectId(Number(event.target.value))}
                >
                    <option value="" disabled>
                        Select a project
                    </option>
                    {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                            {project.title}
                        </option>
                    ))}
                </select>
            </div>

            {error && (
                <div className="mb-6 rounded-2xl bg-red-50 border border-red-200 p-4 text-red-700">
                    {error}
                </div>
            )}

            <div className="bg-white rounded-3xl shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Media Items</h2>

                {loading ? (
                    <p>Loading media...</p>
                ) : mediaItems.length === 0 ? (
                    <p className="text-slate-500">No images found for the selected project.</p>
                ) : (
                    <div className="space-y-4">
                        {mediaItems.map((item) => (
                            <div key={item.id} className="border rounded-2xl p-4">
                                <div className="flex flex-wrap items-center gap-4">
                                    <span className="font-semibold text-slate-700">{item.title || item.file_name}</span>
                                    <span className="text-sm text-slate-500">{item.media_type}</span>
                                    <span className="text-sm text-slate-500">{item.status}</span>
                                </div>
                                <div className="mt-3 text-sm text-slate-700">
                                    {item.file_url ? (
                                        <a
                                            href={item.file_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-blue-600 hover:underline"
                                        >
                                            Open media
                                        </a>
                                    ) : (
                                        <span>{item.file_path}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
