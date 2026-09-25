import api from "./axios";

export const getSocialConnections = async () => (await api.get("/social-connections/")).data;
export const connectSocial = async provider => (await api.post(`/social-connections/${provider}/connect`, {}, { withCredentials: true })).data;
export const disconnectSocial = async id => (await api.delete(`/social-connections/${id}`)).data;
export const getPostingEvents = async id => (await api.get(`/schedules/${id}/events`)).data;
