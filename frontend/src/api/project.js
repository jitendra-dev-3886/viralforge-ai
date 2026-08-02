// src/api/project.js

import api from "./axios";

// ==========================================================
// Create Project
// ==========================================================

export const createProject = async (payload) => {
    const response = await api.post("/projects/", payload);
    return response.data;
};

// ==========================================================
// Get All Projects
// ==========================================================

export const getProjects = async () => {
    const response = await api.get("/projects/");
    return response.data;
};

// ==========================================================
// Get Single Project
// ==========================================================

export const getProject = async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
};

// ==========================================================
// Update Project
// ==========================================================

export const updateProject = async (projectId, payload) => {
    const response = await api.put(`/projects/${projectId}`, payload);
    return response.data;
};

// ==========================================================
// Delete Project
// ==========================================================

export const deleteProject = async (projectId) => {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
};