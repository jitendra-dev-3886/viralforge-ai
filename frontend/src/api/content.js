import api from "./axios";

export const createContent = async (payload, userId = 1) => {
    const response = await api.post(`/content/?user_id=${userId}`, payload);
    return response.data;
};

export const getAllContents = async (userId = 1) => {
    const response = await api.get("/content/", {
        params: { user_id: userId },
    });
    return response.data;
};

export const getContent = async (contentId, userId = 1) => {
    const response = await api.get(`/content/${contentId}`, {
        params: { user_id: userId },
    });
    return response.data;
};

export const getProjectContents = async (projectId, userId = 1) => {
    const response = await api.get(`/content/project/${projectId}`, {
        params: { user_id: userId },
    });
    return response.data;
};

export const updateContent = async (contentId, payload, userId = 1) => {
    const response = await api.put(`/content/${contentId}?user_id=${userId}`, payload);
    return response.data;
};

export const deleteContent = async (contentId, userId = 1) => {
    const response = await api.delete(`/content/${contentId}`, {
        params: { user_id: userId },
    });
    return response.data;
};
