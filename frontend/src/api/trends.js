import api from "./axios";

export const getTrending = async (niche, limit = 24) => {
    const response = await api.get("/trends/", {
        params: niche ? { niche, limit } : { limit },
    });
    return response.data;
};
