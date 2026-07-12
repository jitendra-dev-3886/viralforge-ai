import api from "./axios";

export async function generateContent(data) {

    const response = await api.post(
        "/ai/generate",
        data
    );

    return response.data;
}