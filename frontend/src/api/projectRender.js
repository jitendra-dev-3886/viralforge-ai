import api from "./axios";

export const generateProjectRender = async (projectId) => {
    const response = await api.post("/project-render/generate", {
        project_id: projectId,
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
