import api from "./axios";

export const getAnalytics = async (projectId) => (
    await api.get("/analytics/", { params: projectId ? { project_id: projectId } : {} })
).data;
