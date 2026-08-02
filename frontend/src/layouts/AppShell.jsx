import { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { AuthContext } from "../context/AuthContext";

export default function AppShell() {
    const { isAuthenticated, loading } = useContext(AuthContext);

    if (loading) return null;
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    return (
        <div className="min-h-screen bg-slate-50 lg:flex">
            <Sidebar />
            <div className="min-w-0 flex-1">
                <Topbar />
                <main className="mx-auto w-full max-w-[1600px] p-4 sm:p-6 lg:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
