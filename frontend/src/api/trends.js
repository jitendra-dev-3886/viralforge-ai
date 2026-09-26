import api from "./axios";

export const getTrending = async (niche, limit = 10, context = {}) => {
    const response = await api.get("/trends/", {
        params: { niche, limit, ...context },
    });
    return response.data;
};
