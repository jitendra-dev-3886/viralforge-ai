import { useState } from "react";
import api from "../../api/axios";


export default function Register(){

    const [name,setName] = useState("");
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");

    const [message,setMessage] = useState("");
    const [error,setError] = useState("");


    const handleSubmit = async(e)=>{

        e.preventDefault();

        setMessage("");
        setError("");

        try{

            const response = await api.post(
                "/auth/register",
                {
                    name,
                    email,
                    password
                }
            );


            console.log(
                "REGISTER RESPONSE:",
                response.data
            );


            setMessage(
                "Registration successful"
            );


        }catch(err){

            console.log(err);

            setError(
                err.response?.data?.detail ||
                "Registration failed"
            );

        }

    };


    return (

        <div style={{
            width:"400px",
            margin:"80px auto",
            padding:"30px",
            border:"1px solid #ddd",
            borderRadius:"10px"
        }}>


            <h2>
                Create Account
            </h2>


            {
                message &&
                <p style={{color:"green"}}>
                    {message}
                </p>
            }


            {
                error &&
                <p style={{color:"red"}}>
                    {error}
                </p>
            }


            <form onSubmit={handleSubmit}>


                <input
                    type="text"
                    placeholder="Name"
                    value={name}
                    onChange={(e)=>setName(e.target.value)}
                    required
                />


                <br/><br/>


                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e)=>setEmail(e.target.value)}
                    required
                />


                <br/><br/>


                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                    required
                />


                <br/><br/>


                <button type="submit">
                    Register
                </button>


            </form>


        </div>

    );
}