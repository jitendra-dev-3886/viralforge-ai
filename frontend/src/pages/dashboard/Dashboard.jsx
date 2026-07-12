import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  LayoutDashboard,
  Wand2,
  History,
  BarChart3,
  Settings,
  Users,
  CalendarDays,
  LogOut,
  Sparkles,
} from "lucide-react";

import api from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useContext(AuthContext);

  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (err) {
      console.log(err);
    }

    logout();

    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-100 flex">

      {/* Sidebar */}

      <aside className="w-72 bg-slate-900 text-white flex flex-col">

        <div className="p-6 border-b border-slate-800">

          <div className="flex items-center gap-3">

            <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center">
              <Sparkles size={24} />
            </div>

            <div>
              <h1 className="text-2xl font-bold">
                ViralForge AI
              </h1>

              <p className="text-sm text-slate-400">
                AI Content Automation
              </p>
            </div>

          </div>

        </div>

        <nav className="flex-1 p-5 space-y-2">

          <Link
            to="/dashboard"
            className="flex items-center gap-3 bg-blue-600 rounded-xl px-4 py-3"
          >
            <LayoutDashboard size={20} />
            Dashboard
          </Link>

          {/* <Link
            to="/templates"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <Wand2 size={20} />
            AI Generator
          </Link> */}
          <Link
    to="/ai-studio"
    className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
>
    <Wand2 size={20} />
    AI Studio
</Link>

          <Link
            to="/brands"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <Users size={20} />
            Brands
          </Link>

          <Link
            to="/scheduler"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <CalendarDays size={20} />
            Scheduler
          </Link>

          <Link
            to="/history"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <History size={20} />
            History
          </Link>

          <Link
            to="/analytics"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <BarChart3 size={20} />
            Analytics
          </Link>

          <Link
            to="/settings"
            className="flex items-center gap-3 hover:bg-slate-800 rounded-xl px-4 py-3"
          >
            <Settings size={20} />
            Settings
          </Link>

        </nav>

        <div className="p-5 border-t border-slate-800">

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 transition text-white font-semibold py-3 rounded-xl"
          >
            <LogOut size={18} />
            Logout
          </button>

        </div>

      </aside>

      {/* Main Content */}

      <main className="flex-1 p-8">

        <div className="flex justify-between items-center mb-8">

          <div>

            <h2 className="text-4xl font-bold text-slate-800">
              Dashboard
            </h2>

            <p className="text-slate-500 mt-2">
              Welcome back,
              <span className="font-semibold text-blue-600">
                {" "}{user?.name || "User"}
              </span>
            </p>

          </div>

        </div>

        {/* Statistics */}

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

          <div className="bg-white rounded-2xl shadow p-6">

            <p className="text-slate-500">
              AI Content Generated
            </p>

            <h3 className="text-4xl font-bold mt-3">
              125
            </h3>

          </div>

          <div className="bg-white rounded-2xl shadow p-6">

            <p className="text-slate-500">
              Scheduled Posts
            </p>

            <h3 className="text-4xl font-bold mt-3">
              18
            </h3>

          </div>

          <div className="bg-white rounded-2xl shadow p-6">

            <p className="text-slate-500">
              Published
            </p>

            <h3 className="text-4xl font-bold mt-3">
              76
            </h3>

          </div>

          <div className="bg-white rounded-2xl shadow p-6">

            <p className="text-slate-500">
              Connected Brands
            </p>

            <h3 className="text-4xl font-bold mt-3">
              4
            </h3>

          </div>

        </div>

        {/* Quick Actions */}

        <div className="mt-10">

          <h3 className="text-2xl font-bold mb-5">
            Quick Actions
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            <Link
              to="/generate"
              className="bg-white rounded-2xl shadow p-6 hover:shadow-xl transition"
            >

              <h4 className="text-xl font-semibold">
                ✍ Generate Content
              </h4>

              <p className="mt-3 text-slate-500">
                AI Blogs, Reels, Shorts, Carousels & Captions.
              </p>

            </Link>

            <Link
              to="/scheduler"
              className="bg-white rounded-2xl shadow p-6 hover:shadow-xl transition"
            >

              <h4 className="text-xl font-semibold">
                📅 Schedule Posts
              </h4>

              <p className="mt-3 text-slate-500">
                Publish automatically to all connected platforms.
              </p>

            </Link>

            <Link
              to="/analytics"
              className="bg-white rounded-2xl shadow p-6 hover:shadow-xl transition"
            >

              <h4 className="text-xl font-semibold">
                📈 Analytics
              </h4>

              <p className="mt-3 text-slate-500">
                Track engagement and viral performance.
              </p>

            </Link>

          </div>

        </div>

      </main>

    </div>
  );
}