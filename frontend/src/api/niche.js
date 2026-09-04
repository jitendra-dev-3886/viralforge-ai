import api from "./axios";

export const getNiches = async (includeInactive = false) => {
    const { data } = await api.get("/niches/", { params: { include_inactive: includeInactive } });
    return data;
};
export const createNiche = async (payload) => (await api.post("/niches/", payload)).data;
export const updateNiche = async (id, payload) => (await api.put(`/niches/${id}`, payload)).data;
export const deleteNiche = async (id) => (await api.delete(`/niches/${id}`)).data;
