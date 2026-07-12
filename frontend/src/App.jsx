import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/home/Home";
import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import Register from "./pages/auth/Register";
import AIStudio from "./pages/ai/AIStudio";
import ForgotPassword from "./pages/auth/ForgotPassword";
import Templates from "./pages/ai/Templates";




function App(){
 
    return (
        <BrowserRouter>

            <Routes>

                <Route 
                    path="/" 
                    element={<Home/>}
                />

                <Route 
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/dashboard"
                    element={<Dashboard />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/forgot-password"
                    element={<ForgotPassword />}
                />

                <Route
                    path="/templates"
                    element={<Templates />}
                />

                <Route
    path="ai-studio"
    element={<AIStudio />}
/>

            </Routes>



        </BrowserRouter>
    )
}

export default App;