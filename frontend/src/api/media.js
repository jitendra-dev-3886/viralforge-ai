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
    let response;
    try {
        response = await api.post(
        "/media/download",
        { media_ids: mediaIds },
        { responseType: "blob" },
        );
    } catch (error) {
        let message = "Unable to download the selected files. Please try again.";
        const data = error.response?.data;
        if (data instanceof Blob) {
            try {
                const detail = JSON.parse(await data.text()).detail;
                if (typeof detail === "string") message = detail;
            } catch { /* Keep a useful message for non-JSON server errors. */ }
        } else if (typeof data?.detail === "string") message = data.detail;
        throw new Error(message, { cause: error });
    }

    const contentDisposition = response.headers["content-disposition"] || "";
    let fileName = contentDisposition.match(/filename="?([^";]+)"?/i)?.[1]
        || (mediaIds.length === 1 ? "viralforge-media" : "viralforge-selected-media.zip");
    const encodedName = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
    if (encodedName) {
        try { fileName = decodeURIComponent(encodedName); } catch { /* Use the plain filename. */ }
    }
    fileName = fileName.split(/[\\/]/).pop();
    const url = URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
};
