import { useEffect, useState } from "react";
import { getProjects } from "../../api/project";
import { getProjectContents } from "../../api/content";
import { getContentScenes } from "../../api/scene";
import { generateVoice, getProjectVoices } from "../../api/voice";

export default function VoicePage() {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [contents, setContents] = useState([]);
    const [scenes, setScenes] = useState([]);
    const [contentId, setContentId] = useState("");
    const [sceneId, setSceneId] = useState("");
    const [text, setText] = useState("");
    const [response, setResponse] = useState(null);
    const [projectVoices, setProjectVoices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadProjects = async () => {
            try {
                const { projects: loadedProjects } = await getProjects();
                setProjects(loadedProjects || []);
                if (loadedProjects?.length > 0) {
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
            setContents([]);
            setContentId("");
            return;
        }

        const loadContents = async () => {
            try {
                const response = await getProjectContents(selectedProjectId);
                const loadedContents = response.contents || response || [];
                setContents(loadedContents);
                setContentId(loadedContents[0]?.id || "");
            } catch (err) {
                console.error(err);
                setContents([]);
                setContentId("");
            }
        };

        loadContents();
    }, [selectedProjectId]);

    useEffect(() => {
        if (!contentId) {
            setScenes([]);
            setSceneId("");
            return;
        }

        const loadScenes = async () => {
            try {
                const response = await getContentScenes(contentId);
                const loadedScenes = response.scenes || response || [];
                setScenes(loadedScenes);
                setSceneId(loadedScenes[0]?.id || "");
            } catch (err) {
                console.error(err);
                setScenes([]);
                setSceneId("");
            }
        };

        loadScenes();
    }, [contentId]);

    useEffect(() => {
        if (!selectedProjectId) {
            setProjectVoices([]);
            return;
        }

        const loadVoices = async () => {
            try {
                const response = await getProjectVoices(selectedProjectId);
                setProjectVoices(response.voices || []);
            } catch (err) {
                console.error(err);
            }
        };

        loadVoices();
    }, [selectedProjectId]);

    const handleGenerate = async () => {
        if (!selectedProjectId || !contentId || !sceneId || !text.trim()) {
            setError("Please select a project, content, scene, and enter the voice text.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const payload = {
                project_id: selectedProjectId,
                content_id: Number(contentId),
                scene_id: Number(sceneId),
                provider: "edge-tts",
                voice: "en-US-AriaNeural",
                language: "English",
                speed: "+0%",
                pitch: "+0Hz",
                text,
            };

            const result = await generateVoice(payload);
            setResponse(result);
            const voices = await getProjectVoices(selectedProjectId);
            setProjectVoices(voices.voices || []);
        } catch (err) {
            console.error(err);
            setError("Voice generation failed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">Voice Generation</h1>

            <div className="grid gap-6 lg:grid-cols-2 mb-8">
                <div className="bg-white rounded-3xl shadow-lg p-6">
                    <h2 className="text-xl font-bold mb-4">Generate New Voice</h2>

                    <div className="space-y-4">
                        <div>
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

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Content</label>
                            <select
                                value={contentId}
                                className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                                onChange={(event) => setContentId(Number(event.target.value))}
                                disabled={!selectedProjectId || contents.length === 0}
                            >
                                <option value="" disabled>
                                    {contents.length ? "Select content" : "No content available"}
                                </option>
                                {contents.map((content) => (
                                    <option key={content.id} value={content.id}>
                                        {content.title || `Content ${content.id}`}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Scene</label>
                            <select
                                value={sceneId}
                                className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                                onChange={(event) => setSceneId(Number(event.target.value))}
                                disabled={!contentId || scenes.length === 0}
                            >
                                <option value="" disabled>
                                    {scenes.length ? "Select scene" : "No scenes available"}
                                </option>
                                {scenes.map((scene, index) => (
                                    <option key={scene.id} value={scene.id}>
                                        {scene.title || `Scene ${scene.scene_number || index + 1}`}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Voice Text</label>
                            <textarea
                                rows={4}
                                value={text}
                                onChange={(event) => setText(event.target.value)}
                                className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                                placeholder="Enter the text to render as speech"
                            />
                        </div>

                        {error && (
                            <div className="rounded-2xl bg-red-50 border border-red-200 p-4 text-red-700">
                                {error}
                            </div>
                        )}

                        <button
                            onClick={handleGenerate}
                            className="w-full rounded-2xl bg-indigo-600 px-5 py-3 text-white hover:bg-indigo-700"
                            disabled={loading}
                        >
                            {loading ? "Generating voice..." : "Generate Voice"}
                        </button>
                    </div>
                </div>

                <div className="bg-white rounded-3xl shadow-lg p-6">
                    <h2 className="text-xl font-bold mb-4">Project Voice Records</h2>
                    {projectVoices.length === 0 ? (
                        <p className="text-slate-500">No voices generated for this project yet.</p>
                    ) : (
                        <div className="space-y-4">
                            {projectVoices.map((voice) => (
                                <div key={voice.id} className="border rounded-2xl p-4">
                                    <div className="flex flex-wrap gap-3 items-center text-sm text-slate-600">
                                        <span>{voice.provider}</span>
                                        <span>{voice.language}</span>
                                        <span>Status: {voice.status}</span>
                                    </div>
                                    <p className="mt-3 text-slate-700">{voice.text}</p>
                                    {voice.audio_url && (
                                        <a
                                            href={voice.audio_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-blue-600 hover:underline"
                                        >
                                            Listen to generated audio
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {response && (
                <div className="bg-white rounded-3xl shadow-lg p-6">
                    <h2 className="text-xl font-bold mb-4">Generated Voice Result</h2>
                    <p className="text-slate-700">{response.message || "Voice generation completed."}</p>
                    {response.voice && (
                        <div className="mt-4 space-y-2 text-slate-700">
                            <div>ID: {response.voice.id}</div>
                            <div>Status: {response.voice.status}</div>
                            <div>Audio: {response.voice.audio_url || response.voice.file_path}</div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
