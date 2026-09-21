import api from "./axios";

export const generateProjectRender = async (projectId, contentId) => {
    const response = await api.post("/project-render/generate", {
        project_id: projectId,
        content_id: contentId || null,
    }, { headers: { "Idempotency-Key": crypto.randomUUID() } });
    return response.data;
};

export const uploadProjectMusic = async (projectId, file, workspace = false) => {
    const form = new FormData();
    form.append("file", file);
    form.append("workspace", String(workspace));
    const response = await api.post(`/project-render/music/${projectId}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
};

export const generateProjectRenderById = async (projectId) => {
    const response = await api.get(`/project-render/generate/${projectId}`);
    return response.data;
};

export const getFinalProjectVideo = async (projectId) => {
    const response = await api.get(`/project-render/${projectId}`);
    return response.data;
};
