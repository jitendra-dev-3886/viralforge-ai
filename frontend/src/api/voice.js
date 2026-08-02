import api from "./axios";

export const generateVoice = async (payload) => {
    const response = await api.post("/voice/generate", payload);
    return response.data;
};

export const getVoice = async (voiceId) => {
    const response = await api.get(`/voice/${voiceId}`);
    return response.data;
};

export const getAllVoices = async () => {
    const response = await api.get("/voice/");
    return response.data;
};

export const getProjectVoices = async (projectId) => {
    const response = await api.get(`/voice/project/${projectId}`);
    return response.data;
};

export const getSceneVoice = async (sceneId) => {
    const response = await api.get(`/voice/scene/${sceneId}`);
    return response.data;
};

export const updateVoice = async (voiceId, payload) => {
    const response = await api.put(`/voice/${voiceId}`, payload);
    return response.data;
};

export const deleteVoice = async (voiceId) => {
    const response = await api.delete(`/voice/${voiceId}`);
    return response.data;
};

export const regenerateVoice = async (voiceId) => {
    const response = await api.post(`/voice/${voiceId}/regenerate`);
    return response.data;
};
