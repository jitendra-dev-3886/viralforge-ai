import { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {

    const [user, setUser] = useState(
        JSON.parse(localStorage.getItem("user")) || null
    );

    const [token, setToken] = useState(
        localStorage.getItem("token") || null
    );

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(false);
    }, []);

    const login = (userData, accessToken) => {

        localStorage.setItem(
            "token",
            accessToken
        );

        localStorage.setItem(
            "user",
            JSON.stringify(userData)
        );

        setToken(accessToken);
        setUser(userData);
    };

    const logout = () => {

        localStorage.removeItem("token");
        localStorage.removeItem("user");

        setToken(null);
        setUser(null);
    };

    return (

        <AuthContext.Provider
            value={{
                user,
                token,
                loading,
                login,
                logout,
                isAuthenticated: !!token,
            }}
        >

            {children}

        </AuthContext.Provider>

    );

}