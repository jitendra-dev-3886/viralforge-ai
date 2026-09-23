import PilotPlans from "./PilotPlans";
import { useEffect, useState } from "react";
import { deleteAdminUser, getAdminOverview, getAdminResources, getAdminUsers, updateAdminUser } from "../../api/admin";
import DataTable from "../../components/DataTable";
import DeleteButton from "../../components/DeleteButton";

export default function AdminDashboard() {
  const [counts,setCounts]=useState({}); const [users,setUsers]=useState([]); const [resources,setResources]=useState({}); const [tab,setTab]=useState("users"); const [error,setError]=useState("");
  const load=async()=>{try{const[o,u,r]=await Promise.all([getAdminOverview(),getAdminUsers(),getAdminResources()]);setCounts(o.counts);setUsers(u.users);setResources(r);setError("");}catch(e){setError(e.response?.data?.detail||"Unable to load admin data.");}}; useEffect(()=>{load();},[]);
  const change=async(id,payload)=>{try{await updateAdminUser(id,payload);await load();}catch(e){setError(e.response?.data?.detail||"Update failed.");}};
  const userColumns=[
    {key:"name",label:"User",render:u=><div><strong>{u.name}</strong><div className="text-xs text-slate-500">{u.email}</div></div>,searchValue:u=>`${u.name} ${u.email}`},
    {key:"created_at",label:"Created",render:u=>new Date(u.created_at).toLocaleDateString()},
    {key:"is_active",label:"Status",render:u=><button onClick={()=>change(u.id,{is_active:!u.is_active})} className={`rounded-lg px-3 py-1 ${u.is_active?"bg-emerald-100 text-emerald-700":"bg-red-100 text-red-700"}`}>{u.is_active?"Active":"Disabled"}</button>},
    {key:"is_verified",label:"Verification",render:u=><button onClick={()=>change(u.id,{is_verified:!u.is_verified})} className="rounded-lg border px-3 py-1">{u.is_verified?"Verified":"Unverified"}</button>},
    {key:"is_super_admin",label:"Role",render:u=><button onClick={()=>change(u.id,{is_super_admin:!u.is_super_admin})} className={`rounded-lg px-3 py-1 ${u.is_super_admin?"bg-indigo-100 text-indigo-700":"border"}`}>{u.is_super_admin?"Admin":"User"}</button>},
    {key:"actions",label:"Actions",render:u=>u.delete_blocked_reason
      ? <span className="text-xs text-slate-500">{u.delete_blocked_reason}</span>
      : <DeleteButton label={`user ${u.email}`} description="The account and its linked database records, including projects, content, schedules, and settings, will be permanently deleted. Stored media files and external posts are not removed." onDelete={()=>deleteAdminUser(u.id)} onDeleted={()=>{setUsers(current=>current.filter(user=>user.id!==u.id));load();}} />},
  ];
  const resourceColumns={brands:[{key:"id",label:"ID"},{key:"name",label:"Brand"},{key:"user_id",label:"Owner ID"},{key:"niche",label:"Niche"}],projects:[{key:"id",label:"ID"},{key:"title",label:"Project"},{key:"user_id",label:"Owner ID"},{key:"status",label:"Status"}],contents:[{key:"id",label:"ID"},{key:"title",label:"Content"},{key:"user_id",label:"Owner ID"},{key:"content_type",label:"Format"},{key:"status",label:"Status"}]};
  return <div className="p-1 sm:p-4 lg:p-8"><h1 className="text-3xl font-bold">Super Admin</h1><p className="mt-2 text-slate-500">Searchable platform-wide controls and records.</p>{error&&<p className="mt-4 rounded-xl bg-red-50 p-3 text-red-700">{error}</p>}<div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">{Object.entries(counts).map(([key,value])=><div key={key} className="rounded-2xl bg-white p-5 shadow-sm"><p className="text-xs uppercase text-slate-500">{key}</p><strong className="text-3xl">{value}</strong></div>)}</div><PilotPlans users={users} /><section className="mt-6 rounded-2xl bg-white p-5 shadow-sm"><div className="mb-5 flex flex-wrap gap-2">{["users","brands","projects","contents"].map(name=><button key={name} onClick={()=>setTab(name)} className={`rounded-xl px-4 py-2 text-sm font-semibold capitalize ${tab===name?"bg-indigo-600 text-white":"bg-slate-100"}`}>{name}</button>)}</div>{tab==="users"?<DataTable rows={users} columns={userColumns} searchPlaceholder="Search name or email…"/>:<DataTable rows={resources[tab]||[]} columns={resourceColumns[tab]} searchPlaceholder={`Search ${tab}…`}/>}</section></div>;
}
