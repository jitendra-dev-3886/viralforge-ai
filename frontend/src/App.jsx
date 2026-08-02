import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/home/Home";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";

import Dashboard from "./pages/dashboard/Dashboard";

import AIStudio from "./pages/ai/AIStudio";
import Templates from "./pages/ai/Templates";
import BrandPage from "./pages/brand/BrandPage";
import CreateBrand from "./pages/brand/CreateBrand";
import EditBrand from "./pages/brand/EditBrand";
import ProjectList from "./pages/Project/ProjectList";
import ProjectCreate from "./pages/Project/ProjectCreate";
import ProjectEdit from "./pages/Project/ProjectEdit";
import ProjectDetail from "./pages/Project/ProjectDetail";
import Generate from "./pages/content/Generate";
import ImagesPage from "./pages/images/Images";
import VoicePage from "./pages/voice/Voice";
import RenderPage from "./pages/render/Render";
import DownloaderPage from "./pages/downloader/Downloader";
import ScenesPage from "./pages/scenes/Scenes";
import SubtitlePage from "./pages/subtitle/Subtitle";
import ExportPage from "./pages/export/Export";
import HistoryPage from "./pages/history/HistoryPage";
import Analytics from "./pages/analytics/Analytics";
import SettingsPage from "./pages/settings/SettingsPage";
import Scheduler from "./pages/settings/Scheduler";
import AppShell from "./layouts/AppShell";

import { BrandProvider } from "./context/BrandContext";
import { ProjectProvider } from "./context/ProjectContext";

function App() {

    return (

        <ProjectProvider>
            <BrandProvider>

                <BrowserRouter>

                    <Routes>

                    <Route
                        path="/"
                        element={<Home />}
                    />

                    <Route
                        path="/login"
                        element={<Login />}
                    />

                    <Route
                        path="/register"
                        element={<Register />}
                    />

                    <Route
                        path="/forgot-password"
                        element={<ForgotPassword />}
                    />

                    <Route element={<AppShell />}>

                    <Route
                        path="/dashboard"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/projects"
                        element={<ProjectList />}
                    />

                    <Route
                        path="/projects/create"
                        element={<ProjectCreate />}
                    />

                    <Route
                        path="/projects/:id/edit"
                        element={<ProjectEdit />}
                    />

                    <Route
                        path="/projects/:id"
                        element={<ProjectDetail />}
                    />

                    <Route
                        path="/generate"
                        element={<Generate />}
                    />

                    <Route
                        path="/images"
                        element={<ImagesPage />}
                    />

                    <Route
                        path="/media"
                        element={<ImagesPage />}
                    />

                    <Route
                        path="/voice"
                        element={<VoicePage />}
                    />

                    <Route
                        path="/render"
                        element={<RenderPage />}
                    />

                    <Route
                        path="/downloader"
                        element={<DownloaderPage />}
                    />

                    <Route
                        path="/scenes"
                        element={<ScenesPage />}
                    />

                    <Route
                        path="/subtitle"
                        element={<SubtitlePage />}
                    />

                    <Route
                        path="/history"
                        element={<HistoryPage />}
                    />

                    <Route
                        path="/analytics"
                        element={<Analytics />}
                    />

                    <Route
                        path="/export"
                        element={<ExportPage />}
                    />

                    <Route
                        path="/settings"
                        element={<SettingsPage />}
                    />

                    <Route
                        path="/scheduler"
                        element={<Scheduler />}
                    />

                    <Route                        path="/brands"
                        element={<BrandPage />}
                    />

                    <Route
                        path="/brands/create"
                        element={<CreateBrand />}
                    />

                    <Route
                        path="/brands/:id/edit"
                        element={<EditBrand />}
                    />

                    <Route
                        path="/templates"
                        element={<Templates />}
                    />

                    <Route
                        path="/ai-studio"
                        element={<AIStudio />}
                    />

                    </Route>

                </Routes>

            </BrowserRouter>

            </BrandProvider>
        </ProjectProvider>

    );

}

export default App;
