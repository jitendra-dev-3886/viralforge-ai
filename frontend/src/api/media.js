import api from "./axios";

export const createMedia = async (payload) => {
    const response = await api.post("/media/", payload);
    return response.data;
};

export const getAllMedia = async (userId = 1) => {
    const response = await api.get("/media/", {
        params: { user_id: userId },
    });
    return response.data;
};

export const getMedia = async (mediaId, userId = 1) => {
    const response = await api.get(`/media/${mediaId}`, {
        params: { user_id: userId },
    });
    return response.data;
};

export const getProjectMedia = async (projectId, userId = 1) => {
    const response = await api.get(`/media/project/${projectId}`, {
        params: { user_id: userId },
    });
    return response.data;
};

export const updateMedia = async (mediaId, payload, userId = 1) => {
    const response = await api.put(`/media/${mediaId}`, payload, {
        params: { user_id: userId },
    });
    return response.data;
};

export const deleteMedia = async (mediaId, userId = 1) => {
    const response = await api.delete(`/media/${mediaId}`, {
        params: { user_id: userId },
    });
    return response.data;
};
