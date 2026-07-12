import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import Register from "./pages/auth/Register";
import AIGenerator from "./pages/ai/AIGenerator";
import ForgotPassword from "./pages/auth/ForgotPassword";




function App(){
 
    return (
        <BrowserRouter>

            <Routes>

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
                    path="/ai-generator"
                    element={<AIGenerator />}
                />

            </Routes>



        </BrowserRouter>
    )
}

export default App;