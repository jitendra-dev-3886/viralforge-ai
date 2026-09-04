import api from "./axios";

export const createMedia = async (payload) => {
    const response = await api.post("/media/", payload);
    return response.data;
};

export const getAllMedia = async () => {
    const response = await api.get("/media/");
    return response.data;
};

export const getMedia = async (mediaId) => {
    const response = await api.get(`/media/${mediaId}`);
    return response.data;
};

export const getProjectMedia = async (projectId) => {
    const response = await api.get(`/media/project/${projectId}`);
    return response.data;
};

export const updateMedia = async (mediaId, payload) => {
    const response = await api.put(`/media/${mediaId}`, payload);
    return response.data;
};

export const deleteMedia = async (mediaId) => {
    const response = await api.delete(`/media/${mediaId}`);
    return response.data;
};

export const downloadMedia = async (mediaIds) => {
    const response = await api.post(
        "/media/download",
        { media_ids: mediaIds },
        { responseType: "blob" },
    );

    const contentDisposition = response.headers["content-disposition"] || "";
    const fileName = contentDisposition.match(/filename="?([^";]+)"?/i)?.[1]
        || (mediaIds.length === 1 ? "viralforge-media" : "viralforge-selected-media.zip");
    const url = URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
};
