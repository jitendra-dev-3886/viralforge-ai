import api from "./axios";

export const getContentScenes = async (contentId) => {
    const response = await api.get(`/scenes/content/${contentId}`);
    return response.data;
};

export const getProjectScenes = async (projectId) => (await api.get(`/scenes/project/${projectId}`)).data;
export const updateScene = async (sceneId, payload) => (await api.put(`/scenes/${sceneId}`, payload)).data;
export const deleteScene = async (sceneId) => (await api.delete(`/scenes/${sceneId}`)).data;
export const downloadSceneMedia = async (sceneId) => (await api.post(`/downloader/${sceneId}`)).data;
export const generateSceneSubtitle = async (sceneId) => (await api.post("/subtitle/generate", { scene_id: sceneId })).data;
export const reorderScenes = async (contentId, sceneIds) => (await api.put(`/scenes/content/${contentId}/reorder`, { scene_ids: sceneIds })).data;
