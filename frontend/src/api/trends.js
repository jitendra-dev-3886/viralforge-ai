import api from "./axios";

export const getTrending = async (niche, limit = 10, context = {}, signal) => {
    const response = await api.get("/trends/", {
        params: { niche, limit, ...context },
        signal,
    });
    return response.data;
};
