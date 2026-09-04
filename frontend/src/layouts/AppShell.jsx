import { useContext, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { AuthContext } from "../context/AuthContext";

export default function AppShell() {
    const { isAuthenticated, loading } = useContext(AuthContext);
    const [navigationOpen, setNavigationOpen] = useState(false);

    if (loading) return null;
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    return (
        <div className="min-h-screen bg-slate-50 lg:flex">
            <Sidebar open={navigationOpen} onClose={() => setNavigationOpen(false)} />
            <div className="min-w-0 flex-1">
                <Topbar onMenu={() => setNavigationOpen(true)} />
                <main className="mx-auto w-full max-w-[1600px] overflow-x-hidden p-3 sm:p-6 lg:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
