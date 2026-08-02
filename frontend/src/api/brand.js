import api from "./axios";

export const createBrand = async (payload) => {
    const { data } = await api.post("/brands/", payload);
    return data;
};

export const getBrands = async () => {
    const { data } = await api.get("/brands/");
    return data;
};

export const getBrand = async (brandId) => {
    const { data } = await api.get(`/brands/${brandId}`);
    return data;
};

export const updateBrand = async (brandId, payload) => {
    const { data } = await api.put(`/brands/${brandId}`, payload);
    return data;
};

export const deleteBrand = async (brandId) => {
    const { data } = await api.delete(`/brands/${brandId}`);
    return data;
};
