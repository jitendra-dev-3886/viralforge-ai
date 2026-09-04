import axios from "axios";

// Vite only exposes environment variables prefixed with VITE_. Supplying a
// local default keeps the app usable when no frontend/.env file exists.
export const apiOrigin = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const assetUrl = (value) => value?.startsWith("/") ? `${apiOrigin.replace(/\/$/, "")}${value}` : value;

const api = axios.create({
    baseURL: `${apiOrigin.replace(/\/$/, "")}/api`,

    headers:{
        "Content-Type":"application/json",
    },

});


api.interceptors.request.use((config)=>{

    const token = localStorage.getItem("token");

    if(token){
        config.headers.Authorization = 
        `Bearer ${token}`;
    }

    return config;

});


export default api;
