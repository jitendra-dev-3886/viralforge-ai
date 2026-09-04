import api from "./axios";
export const getAdminOverview = async () => (await api.get("/admin/overview")).data;
export const getAdminUsers = async () => (await api.get("/admin/users")).data;
export const updateAdminUser = async (id, payload) => (await api.put(`/admin/users/${id}`, payload)).data;
export const getAdminResources = async () => (await api.get("/admin/resources")).data;
