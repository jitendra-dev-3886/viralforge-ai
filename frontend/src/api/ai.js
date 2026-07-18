import api from "./axios";

export async function generateContent(data) {

    const response = await api.post("/ai/generate", data);

    console.log("API RESPONSE:", response.data);

    return response.data;
}