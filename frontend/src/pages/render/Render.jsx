import { useEffect, useState } from "react";
import { getProjects } from "../../api/project";
import { getProjectContents } from "../../api/content";
import { generateProjectRender, getFinalProjectVideo, uploadProjectMusic } from "../../api/projectRender";
import { assetUrl } from "../../api/axios";

export default function RenderPage() {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [contents, setContents] = useState([]);
    const [selectedContentId, setSelectedContentId] = useState("");
    const [musicFile, setMusicFile] = useState(null);
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

    useEffect(() => {
        if (!selectedProjectId) return;
        getProjectContents(selectedProjectId).then((response) => {
            const items = response.contents || [];
            setContents(items);
            setSelectedContentId(items[0]?.id || "");
        }).catch(() => { setContents([]); setSelectedContentId(""); });
    }, [selectedProjectId]);

    const handleGenerateRender = async () => {
        if (!selectedProjectId) {
            setError("Please select a project first.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            if (musicFile) await uploadProjectMusic(selectedProjectId, musicFile);
            const response = await generateProjectRender(selectedProjectId, selectedContentId);
            setRenderResult(response);
            if (response.success) {
                const finalResponse = await getFinalProjectVideo(selectedProjectId);
                const video = finalResponse.video;
                setFinalVideo(video?.file_url ? { ...video, file_url: `${video.file_url}${video.file_url.includes("?") ? "&" : "?"}v=${Date.now()}` } : video || null);
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Unable to generate project render. Confirm FFmpeg is installed on the backend.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-1 sm:p-4 lg:p-8">
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

            <div className="mb-6 max-w-2xl space-y-4">
                <div><label className="mb-2 block text-sm font-medium text-slate-700">Generated content</label><select value={selectedContentId} onChange={(event) => setSelectedContentId(Number(event.target.value))} className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3"><option value="" disabled>Select content</option>{contents.map((content) => <option key={content.id} value={content.id}>{content.title} — {content.content_type}</option>)}</select></div>
                <div><label className="mb-2 block text-sm font-medium text-slate-700">Background music (optional)</label><input type="file" accept="audio/mpeg,audio/wav,audio/mp4,audio/aac,audio/ogg" onChange={(event) => setMusicFile(event.target.files?.[0] || null)} className="block w-full rounded-2xl border border-slate-300 bg-white p-3 text-sm" /><p className="mt-1 text-xs text-slate-500">Music is looped at low volume beneath scene narration. Maximum 25 MB.</p></div>
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
                    <video controls playsInline className="mb-5 max-h-[70vh] w-full rounded-2xl bg-black" src={assetUrl(finalVideo.file_url)} />
                    <div className="space-y-3 text-slate-700">
                        <div><strong>File Name:</strong> {finalVideo.file_name}</div>
                        <div><strong>Status:</strong> {finalVideo.status}</div>
                        <div className="break-all"><strong>URL:</strong> {assetUrl(finalVideo.file_url) || finalVideo.file_path}</div>
                        <div><strong>MIME Type:</strong> {finalVideo.mime_type}</div>
                        <div><strong>Duration:</strong> {finalVideo.duration || "N/A"} seconds</div>
                    </div>
                </div>
            )}
        </div>
    );
}
