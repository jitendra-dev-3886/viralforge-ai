import {
    LayoutDashboard,
    Sparkles,
    Workflow,
    FolderKanban,
    BadgeCheck,
    Image,
    Mic,
    Video,
    FileText,
    DownloadCloud,
    Layers,
    Type,
    CalendarDays,
    History,
    BarChart3,
    FileOutput,
    Settings,
    ShieldCheck,
    PanelLeftClose,
    PanelLeftOpen,
    X,
} from "lucide-react";

import { NavLink } from "react-router-dom";
import { useState } from "react";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const menus = [
    { name: "Plans & usage", icon: BadgeCheck, path: "/billing" },

    {
        name: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard",
    },

    {
        name: "AI Studio",
        icon: Sparkles,
        path: "/ai-studio",
    },
    { name: "Creation Workspace", icon: Workflow, path: "/creation-workspace" },

    {
        name: "Brands",
        icon: BadgeCheck,
        path: "/brands",
    },

    {
        name: "Projects",
        icon: FolderKanban,
        path: "/projects",
    },

    {
        name: "Content",
        icon: FileText,
        path: "/generate",
    },

    {
        name: "Media",
        icon: Image,
        path: "/media",
    },

    {
        name: "Render",
        icon: Video,
        path: "/render",
    },

    {
        name: "Voice",
        icon: Mic,
        path: "/voice",
    },

    {
        name: "Downloader",
        icon: DownloadCloud,
        path: "/downloader",
    },

    {
        name: "Scenes",
        icon: Layers,
        path: "/scenes",
    },

    {
        name: "Subtitle",
        icon: Type,
        path: "/subtitle",
    },

    {
        name: "Scheduler",
        icon: CalendarDays,
        path: "/scheduler",
    },

    {
        name: "History",
        icon: History,
        path: "/history",
    },

    {
        name: "Analytics",
        icon: BarChart3,
        path: "/analytics",
    },

    {
        name: "Export",
        icon: FileOutput,
        path: "/export",
    },

    {
        name: "Settings",
        icon: Settings,
        path: "/settings",
    },
    { name: "Super Admin", icon: ShieldCheck, path: "/admin", adminOnly: true },

];

export default function Sidebar({ open = false, onClose = () => {} }) {

    const [collapsed, setCollapsed] = useState(false);
    const { user } = useContext(AuthContext);

    return (
        <>
        {open && <button type="button" aria-label="Close navigation" onClick={onClose} className="fixed inset-0 z-30 bg-slate-950/60 lg:hidden" />}
        <aside
            className={`fixed inset-y-0 left-0 z-40 flex min-h-screen w-[min(18rem,85vw)] flex-col bg-slate-900 text-white shadow-2xl transition-transform duration-300 lg:sticky lg:top-0 lg:z-auto lg:translate-x-0 lg:shadow-none ${
                open ? "translate-x-0" : "-translate-x-full"
            } ${collapsed ? "lg:w-20" : "lg:w-72"}`}
        >

            <div className="flex items-center justify-between px-6 h-20 border-b border-slate-800">

                {!collapsed && (

                    <div>

                        <h2 className="text-xl font-bold">

                            ViralForge AI

                        </h2>

                        <p className="text-xs text-slate-400">

                            AI Content Studio

                        </p>

                    </div>

                )}

                <button className="hidden lg:block"
                    onClick={() => setCollapsed(!collapsed)}
                >

                    {collapsed ? (
                        <PanelLeftOpen size={20}/>
                    ) : (
                        <PanelLeftClose size={20}/>
                    )}

                </button>
                <button type="button" className="rounded-lg p-2 hover:bg-slate-800 lg:hidden" onClick={onClose} aria-label="Close navigation"><X size={20} /></button>

            </div>

            <nav className="mt-6 space-y-2 px-3 flex-1">

                {menus
                    .filter((menu) => !menu.hidden && (!menu.adminOnly || user?.is_super_admin))
                    .map((menu) => {

                        const Icon = menu.icon;

                        return (

                        <NavLink

                            key={menu.name}

                            to={menu.path}
                            onClick={onClose}

                            className={({ isActive }) =>

                                `flex items-center gap-4 rounded-xl px-4 py-3 transition

                                ${
                                    isActive
                                        ? "bg-blue-600"
                                        : "hover:bg-slate-800"
                                }`

                            }

                        >

                            <Icon size={20}/>

                            {(!collapsed || open) && (

                                <span>

                                    {menu.name}

                                </span>

                            )}

                        </NavLink>

                    );

                })}

            </nav>

        </aside>
        </>

    );

}
