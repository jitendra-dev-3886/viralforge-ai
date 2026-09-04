import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AlertCircle, CheckCircle2, Eye, EyeOff, Loader2, Lock, Mail, ShieldCheck, User } from "lucide-react";
import api from "../../api/axios";
import AuthLayout from "../../layouts/AuthLayout";
import SocialLogin from "../../components/auth/SocialLogin";

export default function Register() {
  const navigate=useNavigate(); const [showPassword,setShowPassword]=useState(false); const [loading,setLoading]=useState(false); const [message,setMessage]=useState(""); const [error,setError]=useState(""); const [name,setName]=useState(""); const [email,setEmail]=useState(""); const [password,setPassword]=useState("");
  const strength=useMemo(()=>[password.length>=8,/[A-Z]/.test(password),/\d/.test(password),/[^A-Za-z0-9]/.test(password)].filter(Boolean).length,[password]);
  const handleSubmit=async(event)=>{event.preventDefault();setLoading(true);setMessage("");setError("");try{const response=await api.post("/auth/register",{name,email,password});if(response.data.success){setMessage("Your workspace is ready. Taking you to sign in...");setTimeout(()=>navigate("/login"),1200);}else setError(response.data.message||"We couldn't create your account.");}catch(err){setError(err.response?.data?.detail||err.response?.data?.message||"Registration failed. Please try again.");}finally{setLoading(false);}};
  return <AuthLayout mode="register"><div className="auth-card">
    <p className="auth-card__eyebrow">Start free</p><h2>Build your content engine.</h2><p className="auth-card__intro">Create your workspace in under a minute. No credit card required.</p>
    {message&&<div className="auth-alert auth-alert--success" role="status"><CheckCircle2 size={17}/><span>{message}</span></div>}{error&&<div className="auth-alert auth-alert--error" role="alert"><AlertCircle size={17}/><span>{error}</span></div>}
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="auth-field"><span className="auth-field__label">Full name</span><span className="auth-field__control"><User size={17}/><input type="text" autoComplete="name" placeholder="Your full name" value={name} onChange={(e)=>setName(e.target.value)} disabled={loading} required autoFocus/></span></label>
      <label className="auth-field"><span className="auth-field__label">Work email</span><span className="auth-field__control"><Mail size={17}/><input type="email" autoComplete="email" placeholder="you@company.com" value={email} onChange={(e)=>setEmail(e.target.value)} disabled={loading} required/></span></label>
      <label className="auth-field"><span className="auth-field__label">Create password</span><span className="auth-field__control"><Lock size={17}/><input type={showPassword?"text":"password"} autoComplete="new-password" placeholder="At least 8 characters" minLength={8} value={password} onChange={(e)=>setPassword(e.target.value)} disabled={loading} required/><button className="auth-icon-button" type="button" onClick={()=>setShowPassword((value)=>!value)} aria-label={showPassword?"Hide password":"Show password"} title={showPassword?"Hide password":"Show password"}>{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span><span className="password-meter" aria-label={`Password strength ${strength} out of 4`}>{[1,2,3,4].map((level)=><span key={level} className={strength>=level?(strength>=4?"active strong":"active"):""}/>)}</span><span className="password-hint">Use 8+ characters with a number and uppercase letter.</span></label>
      <label className="auth-check"><input type="checkbox" required/><span>I agree to the <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>.</span></label>
      <button className="auth-submit" type="submit" disabled={loading}>{loading?<><Loader2 className="animate-spin" size={17}/> Creating workspace...</>:"Create my free workspace"}</button>
    </form><SocialLogin />
    <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p><p className="auth-security"><ShieldCheck size={14}/> Free to start. Upgrade only when you&apos;re ready.</p>
  </div></AuthLayout>;
}
