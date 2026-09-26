import { useEffect, useState } from "react";
import { getProjects } from "../../api/project";
import { deleteMedia, getProjectMedia } from "../../api/media";
import { assetUrl } from "../../api/axios";
import DeleteButton from "../../components/DeleteButton";

export default function ImagesPage() {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [mediaItems, setMediaItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedIds, setSelectedIds] = useState([]);
    const [deleting, setDeleting] = useState(false);

    const removeItems = (ids) => {
        setMediaItems((items) => items.filter((item) => !ids.includes(item.id)));
        setSelectedIds((selected) => selected.filter((id) => !ids.includes(id)));
    };

    const deleteSelected = async () => {
        setDeleting(true);
        setError(null);
        try {
            const results = await Promise.allSettled(selectedIds.map((id) => deleteMedia(id)));
            const deletedIds = selectedIds.filter((_, index) =>
                results[index].status === "fulfilled" && results[index].value?.success === true);
            removeItems(deletedIds);
            const failedCount = selectedIds.length - deletedIds.length;
            if (failedCount) {
                setError(`${deletedIds.length} deleted. ${failedCount} could not be deleted. The remaining items are still selected; please try again.`);
            }
            return { success: true };
        } finally {
            setDeleting(false);
        }
    };

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
        let active = true;
        setSelectedIds([]);
        if (!selectedProjectId) {
            setMediaItems([]);
            return;
        }

        const loadMedia = async () => {
            setLoading(true);
            setMediaItems([]);
            setError(null);

            try {
                const response = await getProjectMedia(selectedProjectId);
                if (active) setMediaItems(response.media || []);
            } catch (err) {
                console.error(err);
                if (active) setError("Unable to load media for selected project.");
            } finally {
                if (active) setLoading(false);
            }
        };

        loadMedia();
        return () => { active = false; };
    }, [selectedProjectId]);

    return (
        <div className="p-1 sm:p-4 lg:p-8">
            <h1 className="text-3xl font-bold mb-2">Media Library</h1>
            <p className="mb-6 text-slate-500">Manage images, music, audio, and rendered videos for your projects.</p>

            <div className="mb-6 max-w-2xl">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                    Project
                </label>
                <select
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm"
                    value={selectedProjectId || ""}
                    disabled={deleting}
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
                <div role="alert" className="mb-6 rounded-2xl bg-red-50 border border-red-200 p-4 text-red-700">
                    {error}
                </div>
            )}

            <div className="bg-white rounded-3xl shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Media Items</h2>

                {!loading && mediaItems.length > 0 && (
                    <div className="mb-4 flex flex-wrap items-center gap-4">
                        <label className="flex items-center gap-2 text-sm font-medium">
                            <input type="checkbox" className="h-4 w-4 accent-indigo-600"
                                checked={selectedIds.length === mediaItems.length}
                                ref={(input) => { if (input) input.indeterminate = selectedIds.length > 0 && selectedIds.length < mediaItems.length; }}
                                disabled={deleting}
                                onChange={(event) => setSelectedIds(event.target.checked ? mediaItems.map((item) => item.id) : [])} />
                            Select all
                        </label>
                        <span className="text-sm text-slate-500" aria-live="polite">{selectedIds.length} selected</span>
                        <DeleteButton label={`${selectedIds.length} selected media items`}
                            buttonLabel="Delete selected" disabled={deleting || selectedIds.length === 0}
                            description="This deletes the selected items and their local files, and unlinks them from scenes. Files still used by other library records are kept."
                            onDelete={deleteSelected} onDeleted={() => {}} />
                    </div>
                )}

                {loading ? (
                    <p>Loading media...</p>
                ) : mediaItems.length === 0 ? (
                    <p className="text-slate-500">No media found for the selected project.</p>
                ) : (
                    <div className="space-y-4">
                        {mediaItems.map((item) => (
                            <div key={item.id} className="border rounded-2xl p-4">
                                <div className="flex flex-wrap items-center gap-4">
                                    <label className="flex items-center gap-2 font-semibold text-slate-700">
                                        <input type="checkbox" className="h-4 w-4 accent-indigo-600"
                                            checked={selectedIds.includes(item.id)} disabled={deleting}
                                            onChange={(event) => setSelectedIds((ids) => event.target.checked ? [...ids, item.id] : ids.filter((id) => id !== item.id))} />
                                        {item.title || item.file_name || `Media ${item.id}`}
                                    </label>
                                    <span className="text-sm text-slate-500">{item.media_type}</span>
                                    <span className="text-sm text-slate-500">{item.status}</span>
                                    <DeleteButton disabled={deleting} label={item.title || item.file_name || `media ${item.id}`} description="This deletes the item and its local file, and unlinks it from scenes. Files still used by other library records are kept." onDelete={async () => {
                                        setDeleting(true);
                                        try { return await deleteMedia(item.id); }
                                        finally { setDeleting(false); }
                                    }} onDeleted={() => removeItems([item.id])} />
                                </div>
                                <div className="mt-3 text-sm text-slate-700">
                                    {item.file_url ? (
                                        <a
                                            href={assetUrl(item.file_url)}
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
