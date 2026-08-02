import { useEffect, useState } from "react";
import { getProjects } from "../../api/project";
import { generateProjectRender, getFinalProjectVideo } from "../../api/projectRender";

export default function RenderPage() {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [renderResult, setRenderResult] = useState(null);
    const [finalVideo, setFinalVideo] = useState(null);
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
            setFinalVideo(null);
            return;
        }

        const loadFinalVideo = async () => {
            try {
                const response = await getFinalProjectVideo(selectedProjectId);
                setFinalVideo(response.video || null);
            } catch (err) {
                console.error(err);
                setFinalVideo(null);
            }
        };

        loadFinalVideo();
    }, [selectedProjectId]);

    const handleGenerateRender = async () => {
        if (!selectedProjectId) {
            setError("Please select a project first.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await generateProjectRender(selectedProjectId);
            setRenderResult(response);
            if (response.success) {
                const finalResponse = await getFinalProjectVideo(selectedProjectId);
                setFinalVideo(finalResponse.video || null);
            }
        } catch (err) {
            console.error(err);
            setError("Unable to generate project render.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Project Render</h1>

            <div className="mb-6 max-w-2xl">
                <label className="block text-sm font-medium text-slate-700 mb-2">Project</label>
                <select
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                    value={selectedProjectId || ""}
                    onChange={(event) => setSelectedProjectId(Number(event.target.value))}
                >
                    <option value="" disabled>Select a project</option>
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

            <button
                onClick={handleGenerateRender}
                className="rounded-2xl bg-indigo-600 px-5 py-3 text-white hover:bg-indigo-700"
                disabled={loading}
            >
                {loading ? "Generating render..." : "Generate Final Video"}
            </button>

            {renderResult && (
                <div className="mt-8 bg-white rounded-3xl shadow-lg p-6">
                    <h2 className="text-xl font-bold mb-4">Render Response</h2>
                    <pre className="whitespace-pre-wrap text-sm text-slate-700">{JSON.stringify(renderResult, null, 2)}</pre>
                </div>
            )}

            {finalVideo && (
                <div className="mt-8 bg-white rounded-3xl shadow-lg p-6">
                    <h2 className="text-xl font-bold mb-4">Final Video</h2>
                    <div className="space-y-3 text-slate-700">
                        <div><strong>File Name:</strong> {finalVideo.file_name}</div>
                        <div><strong>Status:</strong> {finalVideo.status}</div>
                        <div><strong>URL:</strong> {finalVideo.file_url || finalVideo.file_path}</div>
                        <div><strong>MIME Type:</strong> {finalVideo.mime_type}</div>
                        <div><strong>Duration:</strong> {finalVideo.duration || "N/A"} seconds</div>
                    </div>
                </div>
            )}
        </div>
    );
}
