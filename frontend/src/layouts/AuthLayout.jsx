import { Link } from "react-router-dom";
import { ArrowUpRight, BarChart3, Check, Clock3, Sparkles, WandSparkles } from "lucide-react";
import "./auth-layout.css";

const workflow = [
  { label: "AI campaign brief", icon: WandSparkles, tone: "coral" },
  { label: "7 social posts", icon: Sparkles, tone: "mint" },
  { label: "Ready to publish", icon: Check, tone: "blue" },
];

export default function AuthLayout({ children, mode = "login" }) {
  const isRegister = mode === "register";
  return (
    <main className="auth-page">
      <section className="auth-story" aria-label="ViralForge AI overview">
        <div className="auth-story__top">
          <Link className="auth-brand" to="/" aria-label="ViralForge AI home"><span className="auth-brand__mark"><Sparkles size={20} /></span><span>ViralForge <strong>AI</strong></span></Link>
          <span className="auth-badge"><span /> AI workspace online</span>
        </div>
        <div className="auth-story__content">
          <p className="auth-eyebrow">One workspace. Endless content.</p>
          <h1>{isRegister ? "Turn one idea into a week of growth." : "Your content engine is ready when you are."}</h1>
          <p className="auth-story__lead">Plan, create, and publish high-performing content with an AI team that works at your speed.</p>
          <div className="ai-preview" aria-label="AI campaign workflow preview">
            <div className="ai-preview__header"><div><span className="ai-preview__label">Today&apos;s campaign</span><strong>Product launch</strong></div><span className="ai-preview__score"><BarChart3 size={14} /> 92% match</span></div>
            <div className="ai-preview__prompt"><Sparkles size={18} /><span>Create a launch campaign for our new AI productivity tool...</span><ArrowUpRight size={18} /></div>
            <div className="ai-preview__flow">{workflow.map(({ label, icon: Icon, tone }, index) => <div className="ai-preview__step" key={label}><span className={`ai-preview__icon ai-preview__icon--${tone}`}><Icon size={16} /></span><div><small>0{index + 1}</small><span>{label}</span></div></div>)}</div>
            <div className="ai-preview__footer"><div className="avatar-stack" aria-hidden="true"><span>MK</span><span>JS</span><span>AL</span></div><span>Built for modern marketing teams</span><span className="time-saved"><Clock3 size={14} /> 6h saved</span></div>
          </div>
        </div>
        <p className="auth-story__quote">“ViralForge replaced three disconnected tools and gave us our mornings back.” <strong>— Maya, Growth Lead</strong></p>
      </section>
      <section className="auth-form-panel">
        <div className="auth-mobile-brand"><Link className="auth-brand" to="/"><span className="auth-brand__mark"><Sparkles size={18} /></span><span>ViralForge <strong>AI</strong></span></Link></div>
        <div className="auth-form-wrap">{children}</div>
        <p className="auth-legal">© 2026 ViralForge AI <span>•</span> <a href="#privacy">Privacy</a> <span>•</span> <a href="#terms">Terms</a></p>
      </section>
    </main>
  );
}
