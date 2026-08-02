import api from "./axios";

export const getContentScenes = async (contentId) => {
    const response = await api.get(`/scenes/content/${contentId}`);
    return response.data;
};
