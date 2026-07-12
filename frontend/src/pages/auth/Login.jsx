import { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  Loader2,
} from "lucide-react";

import api from "../../api/axios";
import { AuthContext } from "../../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      if (response.data.success) {
        login(response.data.user, response.data.token);

        navigate("/dashboard");
      }
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Invalid email or password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex">

      {/* LEFT PANEL */}

      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-900 text-white p-14 flex-col justify-between">

        <div>

          <div className="flex items-center gap-3">

            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">

              <Sparkles size={26} />

            </div>

            <div>

              <h1 className="text-3xl font-bold">
                ViralForge AI
              </h1>

              <p className="text-blue-200 text-sm">
                AI Content Automation Platform
              </p>

            </div>

          </div>

          <h2 className="mt-16 text-5xl font-bold leading-tight">
            Create Once.
            <br />
            Publish Everywhere.
          </h2>

          <p className="mt-8 text-lg text-blue-100 leading-8">
            Generate AI posts, reels, blogs,
            captions and automatically publish
            to Instagram, Facebook, YouTube,
            LinkedIn and X.
          </p>

        </div>

        <div className="grid grid-cols-2 gap-5">

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">
              100+
            </h3>
            <p>AI Templates</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">
              10+
            </h3>
            <p>Platforms</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">
              Auto
            </h3>
            <p>Publishing</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">
              AI
            </h3>
            <p>Content Engine</p>
          </div>

        </div>

      </div>

      {/* RIGHT PANEL */}

      <div className="flex-1 flex items-center justify-center bg-slate-100 px-6">

        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-10">

          <div className="text-center">

            <h2 className="text-4xl font-bold text-slate-900">
              Welcome Back
            </h2>

            <p className="text-slate-500 mt-3">
              Login to continue
            </p>

          </div>

          {error && (
            <div className="mt-6 bg-red-100 text-red-600 rounded-lg p-3 text-sm">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-6"
          >

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Email
              </label>

              <div className="relative mt-2">

                <Mail
                  size={18}
                  className="absolute left-4 top-4 text-gray-400"
                />

                <input
                  type="email"
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  required
                />

              </div>

            </div>

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Password
              </label>

              <div className="relative mt-2">

                <Lock
                  size={18}
                  className="absolute left-4 top-4 text-gray-400"
                />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  className="w-full pl-12 pr-12 py-3 rounded-xl border border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) =>
                    setPassword(
                      e.target.value
                    )
                  }
                  required
                />

                <button
                  type="button"
                  className="absolute right-4 top-3"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                >
                  {showPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>

              </div>

            </div>

            <div className="flex justify-between text-sm">

              <label className="flex items-center gap-2">

                <input type="checkbox" />

                Remember me

              </label>

              <Link
                to="/forgot-password"
                className="text-blue-600 hover:underline"
              >
                Forgot Password?
              </Link>

            </div>

            <button
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 flex justify-center items-center gap-2 transition"
            >
              {loading ? (
                <>
                  <Loader2
                    size={18}
                    className="animate-spin"
                  />
                  Logging in...
                </>
              ) : (
                "Login to ViralForge AI"
              )}
            </button>

            <p className="text-center text-slate-600">

              Don't have an account?

              <Link
                to="/register"
                className="ml-2 text-blue-600 font-semibold hover:underline"
              >
                Register
              </Link>

            </p>

          </form>

        </div>

      </div>

    </div>
  );
}