import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AlertCircle, Eye, EyeOff, Loader2, Lock, Mail, ShieldCheck } from "lucide-react";
import api from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";
import AuthLayout from "../../layouts/AuthLayout";
import SocialLogin from "../../components/auth/SocialLogin";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault(); setLoading(true); setError("");
    try {
      const response = await api.post("/auth/login", { email, password });
      if (response.data.success) { login(response.data.user, response.data.token); navigate("/dashboard"); }
      else setError(response.data.message || "We couldn't sign you in. Please check your details.");
    } catch (err) { setError(err.response?.data?.detail || err.response?.data?.message || "Invalid email or password."); }
    finally { setLoading(false); }
  };

  return <AuthLayout mode="login"><div className="auth-card">
    <p className="auth-card__eyebrow">Welcome back</p><h2>Continue creating.</h2>
    <p className="auth-card__intro">Sign in to access your projects, campaigns, and AI workspace.</p>
    {error && <div className="auth-alert auth-alert--error" role="alert"><AlertCircle size={17}/><span>{error}</span></div>}
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="auth-field"><span className="auth-field__label">Work email</span><span className="auth-field__control"><Mail size={17}/><input type="email" autoComplete="email" placeholder="you@company.com" value={email} onChange={(e)=>setEmail(e.target.value)} disabled={loading} required autoFocus/></span></label>
      <label className="auth-field"><span className="auth-field__label"><span>Password</span><Link className="auth-link" to="/forgot-password">Forgot password?</Link></span><span className="auth-field__control"><Lock size={17}/><input type={showPassword?"text":"password"} autoComplete="current-password" placeholder="Enter your password" value={password} onChange={(e)=>setPassword(e.target.value)} disabled={loading} required/><button className="auth-icon-button" type="button" onClick={()=>setShowPassword((value)=>!value)} aria-label={showPassword?"Hide password":"Show password"} title={showPassword?"Hide password":"Show password"}>{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span></label>
      <button className="auth-submit" type="submit" disabled={loading}>{loading?<><Loader2 className="animate-spin" size={17}/> Signing in...</>:"Sign in to ViralForge"}</button>
    </form><SocialLogin />
    <p className="auth-switch">New to ViralForge? <Link to="/register">Start creating free</Link></p>
    <p className="auth-security"><ShieldCheck size={14}/> Your data is encrypted and securely stored.</p>
  </div></AuthLayout>;
}
