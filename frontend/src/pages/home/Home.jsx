import { Link } from "react-router-dom";
import ThemeToggle from "../../components/ThemeToggle";


export default function Home(){

return (

<div className="
min-h-screen
bg-white
dark:bg-slate-950
text-slate-900
dark:text-white
transition
">


{/* NAVBAR */}

<header className="
fixed top-0 w-full z-50
backdrop-blur-xl
bg-white/80
dark:bg-slate-950/80
border-b
border-gray-200
dark:border-slate-800
">

<div className="
max-w-7xl mx-auto
px-3 py-4 sm:px-6
flex justify-between items-center
">


<div className="flex items-center gap-3">


<div className="
w-11 h-11 rounded-xl
bg-gradient-to-r from-purple-600 to-pink-600
flex items-center justify-center
text-white font-bold
">

VF

</div>


<h1 className="
hidden text-2xl font-bold sm:block
">

ViralForge AI

</h1>


</div>



<div className="hidden md:flex gap-8 text-gray-500">

<a>Features</a>
<a>Solutions</a>
<a>Pricing</a>
<a>About</a>

</div>



<div className="flex items-center gap-3">


<ThemeToggle/>


<Link
to="/login"
className="
hidden px-5 py-2 sm:block
rounded-xl
border
dark:border-slate-700
"
>

Login

</Link>


<Link
to="/register"
className="
px-3 py-2 sm:px-5
rounded-xl
bg-purple-600
text-white
"
>

Start Free

</Link>


</div>


</div>


</header>





{/* HERO */}


<section className="
pt-40
max-w-7xl
mx-auto
px-6
grid md:grid-cols-2
gap-16
items-center
">


<div>


<span className="
px-4 py-2
rounded-full
bg-purple-100
dark:bg-purple-500/20
text-purple-600
">

🚀 AI Content Creation Platform

</span>



<h1 className="
mt-8
text-5xl
md:text-6xl
font-bold
leading-tight
">


Create
<span className="text-purple-600">
 Viral Content
</span>

<br/>

Automatically With AI


</h1>



<p className="
mt-6
text-xl
text-gray-500
dark:text-gray-400
">


Generate reels, images,
blogs, captions and social
media content using AI.


</p>



<div className="mt-8 flex gap-4">


<Link
to="/register"
className="
px-8 py-4
rounded-xl
bg-purple-600
text-white
font-semibold
"
>

Start Creating

</Link>



<button
className="
px-8 py-4
rounded-xl
border
dark:border-slate-700
"
>

Watch Demo

</button>


</div>



<div className="
mt-10
flex gap-10
">


<div>
<h3 className="text-3xl font-bold">
50K+
</h3>
<p className="text-gray-500">
Creators
</p>
</div>


<div>
<h3 className="text-3xl font-bold">
1M+
</h3>
<p className="text-gray-500">
Content Generated
</p>
</div>


<div>
<h3 className="text-3xl font-bold">
99%
</h3>
<p className="text-gray-500">
Automation
</p>
</div>


</div>


</div>






{/* PRODUCT PREVIEW */}


<div className="
rounded-3xl
border
dark:border-slate-800
bg-gray-100
dark:bg-slate-900
p-6
shadow-xl
">


<div className="
rounded-2xl
bg-white
dark:bg-slate-950
p-6
">


<div className="
flex justify-between
">

<h3 className="font-bold">
AI Studio
</h3>


<span>
● Online
</span>


</div>



<div className="
mt-6
bg-gray-100
dark:bg-slate-900
rounded-xl
p-5
">

Create Instagram Reel about AI Future


</div>




<div className="
grid grid-cols-2
gap-4
mt-5
">


<Card
icon="✍️"
title="AI Writer"
/>


<Card
icon="🎨"
title="AI Image"
/>


<Card
icon="🎬"
title="Reels"
/>


<Card
icon="📈"
title="SEO"
/>


</div>


</div>


</div>


</section>






{/* FEATURES */}


<section className="
max-w-7xl mx-auto
px-6
py-24
">


<h2 className="
text-4xl
font-bold
text-center
">

Everything you need to grow

</h2>


<div className="
grid md:grid-cols-3
gap-8
mt-12
">


<Feature
title="AI Content Generator"
text="Generate professional content instantly"
/>


<Feature
title="Social Automation"
text="Manage multiple platforms easily"
/>


<Feature
title="Creator Analytics"
text="Track content performance"
/>


</div>


</section>






{/* FOOTER */}


<footer className="
border-t
dark:border-slate-800
py-10
text-center
text-gray-500
">


© 2026 ViralForge AI. All rights reserved.


</footer>


</div>

)

}





function Card({icon,title}){

return (

<div className="
rounded-xl
p-5
bg-gray-100
dark:bg-slate-900
">

<div className="text-3xl">
{icon}
</div>

<p className="mt-3 font-semibold">
{title}
</p>

</div>

)

}




function Feature({title,text}){

return (

<div className="
p-8
rounded-2xl
border
dark:border-slate-800
">

<h3 className="text-xl font-bold">
{title}
</h3>

<p className="mt-3 text-gray-500">
{text}
</p>


</div>

)

}
