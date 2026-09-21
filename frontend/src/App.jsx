import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Home from "./pages/home/Home";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import OAuthCallback from "./pages/auth/OAuthCallback";
import SetPassword from "./pages/auth/SetPassword";

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
import { NicheProvider } from "./context/NicheContext";
import AdminDashboard from "./pages/admin/AdminDashboard";
import ContentEditor from "./pages/content/ContentEditor";
import { lazy, Suspense, useContext } from "react";
import { AuthContext } from "./context/AuthContext";
const BillingPage = lazy(() => import("./pages/settings/BillingPage"));
const CreationWorkspace = lazy(() => import("./pages/workspace/CreationWorkspace"));

function AdminRoute() {
    const { user } = useContext(AuthContext);
    return user?.is_super_admin ? <AdminDashboard /> : <Navigate to="/dashboard" replace />;
}

function App() {

    return (

        <ProjectProvider>
            <BrandProvider>
              <NicheProvider>

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

                    <Route path="/auth/callback" element={<OAuthCallback />} />
                    <Route path="/set-password" element={<SetPassword />} />

                    <Route element={<AppShell />}>
                    <Route path="/billing" element={<Suspense fallback={<p>Loading plans...</p>}><BillingPage /></Suspense>} />
                    <Route path="/creation-workspace" element={<Suspense fallback={<p role="status" className="p-6 text-slate-500">Loading creation workspace...</p>}><CreationWorkspace /></Suspense>} />

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
                    <Route path="/content/:id/edit" element={<ContentEditor />} />

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
                    <Route path="/admin" element={<AdminRoute />} />

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

              </NicheProvider>
            </BrandProvider>
        </ProjectProvider>

    );

}

export default App;
