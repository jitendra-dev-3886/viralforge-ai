import { FaFacebookF, FaGoogle, FaInstagram, FaYoutube } from "react-icons/fa";
import { apiOrigin } from "../../api/axios";

const providers=[{id:"google",label:"Google",icon:FaGoogle},{id:"facebook",label:"Facebook",icon:FaFacebookF},{id:"instagram",label:"Instagram",icon:FaInstagram},{id:"youtube",label:"YouTube",icon:FaYoutube}];
export default function SocialLogin(){const connect=(provider)=>window.location.assign(`${apiOrigin.replace(/\/$/,"")}/api/auth/oauth/${provider}`);return <div className="social-auth"><div className="social-auth__divider"><span>or continue with</span></div><div className="social-auth__grid">{providers.map(({id,label,icon:Icon})=><button key={id} type="button" className={`social-auth__button social-auth__button--${id}`} onClick={()=>connect(id)} aria-label={`Continue with ${label}`}><Icon size={17}/><span>{label}</span></button>)}</div></div>}
