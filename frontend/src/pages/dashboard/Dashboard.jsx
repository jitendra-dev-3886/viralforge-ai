import { useContext } from "react";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    Clapperboard,
    FileText,
    FolderKanban,
    Image,
    Mic,
    Plus,
    Sparkles,
} from "lucide-react";
import { AuthContext } from "../../context/AuthContext";
import { useBrand } from "../../context/BrandContext";
import { useProject } from "../../context/ProjectContext";

const quickActions = [
    {
        title: "New project",
        description: "Set up a workspace for your next campaign.",
        path: "/projects/create",
        icon: FolderKanban,
        tone: "bg-blue-50 text-blue-700",
    },
    {
        title: "Create a brand",
        description: "Add voice, style, and brand details once.",
        path: "/brands/create",
        icon: BadgeCheck,
        tone: "bg-violet-50 text-violet-700",
    },
    {
        title: "Generate content",
        description: "Create scripts, captions, and visual scenes.",
        path: "/generate",
        icon: Sparkles,
        tone: "bg-amber-50 text-amber-700",
    },
    {
        title: "Create voiceover",
        description: "Turn scene copy into natural-sounding speech.",
        path: "/voice",
        icon: Mic,
        tone: "bg-rose-50 text-rose-700",
    },
    {
        title: "Render video",
        description: "Combine scenes into a final export.",
        path: "/render",
        icon: Clapperboard,
        tone: "bg-emerald-50 text-emerald-700",
    },
    {
        title: "Manage media",
        description: "Review images and assets for your projects.",
        path: "/media",
        icon: Image,
        tone: "bg-cyan-50 text-cyan-700",
    },
];

export default function Dashboard() {
    const { user } = useContext(AuthContext);
    const { projects, loading: projectsLoading } = useProject();
    const { brands, loading: brandsLoading } = useBrand();
    const activeProjects = projects.filter((project) => project.status !== "archived");
    const recentProjects = projects.slice(0, 4);

    return (
        <div className="mx-auto max-w-7xl pb-10">
            <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 px-6 py-8 text-white sm:px-8">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-200">ViralForge workspace</p>
                <div className="mt-3 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Welcome back, {user?.name?.split(" ")[0] || "creator"}.</h2>
                        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">Pick up a project or start a new piece of content from one focused workspace.</p>
                    </div>
                    <Link to="/generate" className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-blue-50">
                        <Sparkles size={17} /> Generate content
                    </Link>
                </div>
            </section>

            <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Metric label="Active projects" value={projectsLoading ? "—" : activeProjects.length} icon={FolderKanban} tone="text-blue-600 bg-blue-50" />
                <Metric label="Brand profiles" value={brandsLoading ? "—" : brands.length} icon={BadgeCheck} tone="text-violet-600 bg-violet-50" />
                <Metric label="Ready to generate" value={projectsLoading ? "—" : activeProjects.length} icon={Sparkles} tone="text-amber-600 bg-amber-50" />
                <Metric label="Recent projects" value={projectsLoading ? "—" : recentProjects.length} icon={FileText} tone="text-emerald-600 bg-emerald-50" />
            </section>

            <section className="mt-8">
                <div className="mb-4 flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-slate-900">Quick actions</h3>
                        <p className="mt-1 text-sm text-slate-500">Start the next step without digging through the navigation.</p>
                    </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    {quickActions.map((action) => {
                        const Icon = action.icon;
                        return (
                            <Link key={action.title} to={action.path} className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md">
                                <div className="flex items-start justify-between gap-4">
                                    <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${action.tone}`}><Icon size={20} /></span>
                                    <ArrowRight size={18} className="mt-1 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-blue-600" />
                                </div>
                                <h4 className="mt-4 font-semibold text-slate-900">{action.title}</h4>
                                <p className="mt-1 text-sm leading-5 text-slate-500">{action.description}</p>
                            </Link>
                        );
                    })}
                </div>
            </section>

            <section className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
                    <div>
                        <h3 className="font-semibold text-slate-900">Recent projects</h3>
                        <p className="mt-1 text-sm text-slate-500">Continue from where you left off.</p>
                    </div>
                    <Link to="/projects" className="text-sm font-semibold text-blue-600 hover:text-blue-700">View all</Link>
                </div>
                {projectsLoading ? (
                    <div className="space-y-3 p-5">{[1, 2, 3].map((item) => <div key={item} className="h-12 animate-pulse rounded-xl bg-slate-100" />)}</div>
                ) : recentProjects.length ? (
                    <div className="divide-y divide-slate-100">
                        {recentProjects.map((project) => (
                            <Link key={project.id} to={`/projects/${project.id}`} className="flex items-center justify-between gap-4 px-5 py-4 transition hover:bg-slate-50">
                                <div className="min-w-0">
                                    <p className="truncate font-medium text-slate-800">{project.title}</p>
                                    <p className="mt-1 truncate text-sm text-slate-500">{project.topic}</p>
                                </div>
                                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium capitalize text-slate-600">{project.status || "draft"}</span>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="px-5 py-10 text-center">
                        <FolderKanban size={28} className="mx-auto text-slate-300" />
                        <p className="mt-3 font-medium text-slate-700">No projects yet</p>
                        <Link to="/projects/create" className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-blue-600"><Plus size={16} /> Create your first project</Link>
                    </div>
                )}
            </section>
        </div>
    );
}

function Metric({ label, value, icon: Icon, tone }) {
    return (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${tone}`}><Icon size={18} /></span>
            </div>
            <p className="mt-4 text-3xl font-bold tracking-tight text-slate-900">{value}</p>
        </div>
    );
}
