import api from "./axios";

export const createContent = async (payload) => {
    const response = await api.post("/content/", payload);
    return response.data;
};

export const getAllContents = async (filters = {}) => {
    const response = await api.get("/content/", {
        params: filters,
    });
    return response.data;
};

export const getContent = async (contentId) => {
    const response = await api.get(`/content/${contentId}`);
    return response.data;
};

export const getProjectContents = async (projectId) => {
    const response = await api.get(`/content/project/${projectId}`);
    return response.data;
};

export const updateContent = async (contentId, payload) => {
    const response = await api.put(`/content/${contentId}`, payload);
    return response.data;
};

export const deleteContent = async (contentId) => {
    const response = await api.delete(`/content/${contentId}`);
    return response.data;
};
