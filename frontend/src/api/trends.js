import api from "./axios";

export const getTrending = async (niche) => {
    const response = await api.get("/trends/", {
        params: niche ? { niche } : {},
    });
    return response.data;
};
