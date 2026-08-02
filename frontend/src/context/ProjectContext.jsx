import { createContext, useContext, useEffect, useState } from "react";
import {
    createProject,
    getProjects,
    getProject,
    updateProject as updateProjectApi,
    deleteProject as deleteProjectApi,
} from "../api/project";

const ProjectContext = createContext();

export function ProjectProvider({ children }) {
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [loading, setLoading] = useState(false);

    const loadProjects = async () => {
        try {
            setLoading(true);
            const response = await getProjects();
            setProjects(response.projects || response);
        } catch (error) {
            console.error("Load Projects Error:", error);
        } finally {
            setLoading(false);
        }
    };

    const addProject = async (payload) => {
        const response = await createProject(payload);
        await loadProjects();
        return response;
    };

    const editProject = async (projectId, payload) => {
        const response = await updateProjectApi(projectId, payload);
        await loadProjects();
        return response;
    };

    const removeProject = async (projectId) => {
        const response = await deleteProjectApi(projectId);
        await loadProjects();
        return response;
    };

    const getProjectById = async (projectId) => {
        const response = await getProject(projectId);
        return response.project || response;
    };

    useEffect(() => {
        loadProjects();
    }, []);

    const value = {
        projects,
        loading,
        selectedProject,
        setSelectedProject,
        loadProjects,
        addProject,
        editProject,
        removeProject,
        getProjectById,
    };

    return (
        <ProjectContext.Provider value={value}>
            {children}
        </ProjectContext.Provider>
    );
}

export function useProject() {
    const context = useContext(ProjectContext);
    if (!context) {
        throw new Error("useProject must be used inside ProjectProvider");
    }
    return context;
}
