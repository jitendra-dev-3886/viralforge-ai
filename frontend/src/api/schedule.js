import api from "./axios";
export const getSchedules=async()=>(await api.get("/schedules/")).data;
export const createSchedule=async(payload)=>(await api.post("/schedules/",payload)).data;
export const updateSchedule=async(id,payload)=>(await api.put(`/schedules/${id}`,payload)).data;
export const deleteSchedule=async(id)=>(await api.delete(`/schedules/${id}`)).data;
