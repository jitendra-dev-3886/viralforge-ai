import { useState, useContext } from "react";
import api from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";


export default function Login() {

    const { login } = useContext(AuthContext);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    const handleSubmit = async (e) => {

        e.preventDefault();

        setError("");
        setLoading(true);

        try {

            const response = await api.post(
                "/auth/login",
                {
                    email,
                    password
                }
            );


            if (response.data.success) {

                login(
                    response.data.user,
                    response.data.token
                );


                window.location.href = "/dashboard";
            }


        } catch (err) {

            setError(
                err.response?.data?.message ||
                "Login failed"
            );

        } finally {

            setLoading(false);

        }
    };


    return (

        <div style={{
            width: "400px",
            margin: "80px auto",
            padding: "30px",
            border: "1px solid #ddd",
            borderRadius: "10px"
        }}>

            <h2>
                Login
            </h2>


            {error && (
                <p style={{color:"red"}}>
                    {error}
                </p>
            )}


            <form onSubmit={handleSubmit}>


                <div>
                    <label>
                        Email
                    </label>

                    <input
                        type="email"
                        value={email}
                        onChange={(e)=>setEmail(e.target.value)}
                        placeholder="Enter email"
                        required
                    />

                </div>


                <br/>


                <div>

                    <label>
                        Password
                    </label>

                    <input
                        type="password"
                        value={password}
                        onChange={(e)=>setPassword(e.target.value)}
                        placeholder="Enter password"
                        required
                    />

                </div>


                <br/>


                <button 
                    type="submit"
                    disabled={loading}
                >
                    {loading ? "Logging in..." : "Login"}
                </button>


            </form>

        </div>

    );
}