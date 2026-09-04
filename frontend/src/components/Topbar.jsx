import { useContext, useState } from "react";
import { Bell, ChevronDown, LogOut, Menu, Search, Settings } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";

const pageNames = {
    "/dashboard": "Dashboard",
    "/ai-studio": "AI Studio",
    "/projects": "Projects",
    "/brands": "Brands",
    "/generate": "Content generation",
    "/media": "Media library",
    "/voice": "Voice studio",
    "/render": "Render studio",
    "/settings": "Settings",
};

export default function Topbar({ onMenu }) {
    const { user, logout } = useContext(AuthContext);
    const [menuOpen, setMenuOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const pageName = pageNames[location.pathname] || "Workspace";
    const initials = (user?.name || user?.email || "U")
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

    const handleLogout = async () => {
        try {
            await api.post("/auth/logout");
        } catch {
            // Clearing the local session is sufficient for this stateless JWT flow.
        } finally {
            logout();
            navigate("/login", { replace: true });
        }
    };

    return (
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6">
            <div className="flex min-w-0 items-center gap-2">
                <button type="button" onClick={onMenu} className="shrink-0 rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden" aria-label="Open navigation"><Menu size={22} /></button>
                <div className="min-w-0">
                <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">Workspace</p>
                <h1 className="truncate text-base font-semibold text-slate-900 sm:text-lg">{pageName}</h1>
                </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
                <button type="button" className="hidden items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-400 md:flex">
                    <Search size={16} />
                    <span>Search</span>
                    <kbd className="rounded border border-slate-200 px-1.5 text-xs">⌘K</kbd>
                </button>
                <button type="button" aria-label="Notifications" className="relative rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800">
                    <Bell size={19} />
                    <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-blue-600" />
                </button>

                <div className="relative">
                    <button
                        type="button"
                        onClick={() => setMenuOpen((open) => !open)}
                        className="flex items-center gap-2 rounded-lg p-1.5 text-left transition hover:bg-slate-100"
                        aria-expanded={menuOpen}
                        aria-label="Open account menu"
                    >
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-xs font-bold text-white">{initials}</span>
                        <span className="hidden max-w-36 sm:block">
                            <span className="block truncate text-sm font-semibold text-slate-800">{user?.name || "Account"}</span>
                            <span className="block truncate text-xs text-slate-500">{user?.email || ""}</span>
                        </span>
                        <ChevronDown size={16} className="hidden text-slate-500 sm:block" />
                    </button>

                    {menuOpen && (
                        <div className="absolute right-0 mt-2 w-64 overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl">
                            <div className="border-b border-slate-100 px-4 py-3">
                                <p className="truncate text-sm font-semibold text-slate-800">{user?.name || "Account"}</p>
                                <p className="truncate text-xs text-slate-500">{user?.email || ""}</p>
                            </div>
                            <button type="button" onClick={() => navigate("/settings")} className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50">
                                <Settings size={17} /> Account settings
                            </button>
                            <button type="button" onClick={handleLogout} className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50">
                                <LogOut size={17} /> Log out
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
