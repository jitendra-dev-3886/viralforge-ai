import { useContext, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AlertCircle, Loader2 } from "lucide-react";
import api from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";
import AuthLayout from "../../layouts/AuthLayout";

export default function OAuthCallback(){const[params]=useSearchParams();const navigate=useNavigate();const{login}=useContext(AuthContext);const[error,setError]=useState(params.get("error")||"");useEffect(()=>{const token=new URLSearchParams(window.location.hash.slice(1)).get("token");if(!token||error)return;window.history.replaceState({},"",window.location.pathname);localStorage.setItem("token",token);api.get("/auth/me").then(({data})=>{login(data.user,token);navigate(data.user.has_password?"/dashboard":"/set-password",{replace:true})}).catch((err)=>{localStorage.removeItem("token");setError(err.response?.data?.detail||"Social sign-in could not be completed.")})},[error,login,navigate]);return <AuthLayout><div className="auth-card auth-callback">{error?<><div className="auth-alert auth-alert--error"><AlertCircle size={17}/><span>{error}</span></div><h2>Sign-in interrupted.</h2><p className="auth-card__intro">Return to sign in and try again.</p><Link className="auth-submit" to="/login">Back to sign in</Link></>:<><Loader2 className="animate-spin" size={28}/><h2>Finishing sign-in...</h2><p className="auth-card__intro">We&apos;re securely connecting your workspace.</p></>}</div></AuthLayout>}
