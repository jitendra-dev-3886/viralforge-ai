import { useTheme } from "../context/ThemeContext";


export default function ThemeToggle(){

    const {dark,setDark}=useTheme();


    return (

        <button
            onClick={()=>setDark(!dark)}
            className="
            w-11 h-11
            rounded-full
            border
            flex
            items-center
            justify-center
            bg-white
            dark:bg-slate-900
            "
        >

            {dark ? "☀️" : "🌙"}

        </button>

    )

}