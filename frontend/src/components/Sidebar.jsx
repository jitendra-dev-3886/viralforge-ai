import {
    LayoutDashboard,
    Sparkles,
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
    PanelLeftClose,
    PanelLeftOpen,
} from "lucide-react";

import { NavLink } from "react-router-dom";
import { useState } from "react";

const menus = [

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

    {
        name: "Projects",
        icon: FolderKanban,
        path: "/projects",
    },

    {
        name: "Brands",
        icon: BadgeCheck,
        path: "/brands",
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

];

export default function Sidebar() {

    const [collapsed, setCollapsed] = useState(false);

    return (

        <aside
            className={`min-h-screen bg-slate-900 text-white transition-all duration-300 flex flex-col ${
                collapsed ? "w-20" : "w-72"
            }`}
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

                <button
                    onClick={() => setCollapsed(!collapsed)}
                >

                    {collapsed ? (
                        <PanelLeftOpen size={20}/>
                    ) : (
                        <PanelLeftClose size={20}/>
                    )}

                </button>

            </div>

            <nav className="mt-6 space-y-2 px-3 flex-1">

                {menus
                    .filter((menu) => !menu.hidden)
                    .map((menu) => {

                        const Icon = menu.icon;

                        return (

                        <NavLink

                            key={menu.name}

                            to={menu.path}

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

                            {!collapsed && (

                                <span>

                                    {menu.name}

                                </span>

                            )}

                        </NavLink>

                    );

                })}

            </nav>

        </aside>

    );

}
