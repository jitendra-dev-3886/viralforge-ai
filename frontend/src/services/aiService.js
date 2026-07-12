import api from "../api/axios";

export async function generateContent(payload){

    const response = await api.post(
        "/ai/generate",
        payload
    );

    return response.data;

}