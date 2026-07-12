import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  Loader2,
} from "lucide-react";

import api from "../../api/axios";

export default function Register() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");

  const [error, setError] = useState("");

  const [name, setName] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post("/auth/register", {
        name,
        email,
        password,
      });

      if (response.data.success) {
        setMessage("Registration successful.");

        setTimeout(() => {
          navigate("/login");
        }, 1500);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Registration failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex">

      {/* LEFT PANEL */}

      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-indigo-700 via-blue-700 to-slate-900 text-white p-14 flex-col justify-between">

        <div>

          <div className="flex items-center gap-3">

            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <Sparkles size={26} />
            </div>

            <div>
              <h1 className="text-3xl font-bold">
                ViralForge AI
              </h1>

              <p className="text-blue-200">
                AI Social Media Automation
              </p>
            </div>

          </div>

          <h2 className="text-5xl font-bold mt-16 leading-tight">
            Build Your
            <br />
            AI Marketing Team
          </h2>

          <p className="mt-8 text-blue-100 leading-8">
            Generate AI content,
            schedule posts,
            auto publish reels,
            blogs and social media
            content from one dashboard.
          </p>

        </div>

        <div className="grid grid-cols-2 gap-5">

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">100+</h3>
            <p>Templates</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">AI</h3>
            <p>Writer</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">Auto</h3>
            <p>Posting</p>
          </div>

          <div className="bg-white/10 rounded-xl p-5">
            <h3 className="text-3xl font-bold">Analytics</h3>
            <p>Dashboard</p>
          </div>

        </div>

      </div>

      {/* RIGHT PANEL */}

      <div className="flex-1 flex items-center justify-center bg-slate-100 px-6">

        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-10">

          <div className="text-center">

            <h2 className="text-4xl font-bold text-slate-900">
              Create Account
            </h2>

            <p className="text-slate-500 mt-3">
              Start using ViralForge AI
            </p>

          </div>

          {message && (
            <div className="mt-6 bg-green-100 text-green-700 rounded-lg p-3">
              {message}
            </div>
          )}

          {error && (
            <div className="mt-6 bg-red-100 text-red-700 rounded-lg p-3">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-6"
          >

            <div>

              <label className="text-sm font-semibold">
                Full Name
              </label>

              <div className="relative mt-2">

                <User
                  size={18}
                  className="absolute left-4 top-4 text-gray-400"
                />

                <input
                  type="text"
                  placeholder="Enter your name"
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-600 outline-none"
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                  required
                />

              </div>

            </div>

            <div>

              <label className="text-sm font-semibold">
                Email Address
              </label>

              <div className="relative mt-2">

                <Mail
                  size={18}
                  className="absolute left-4 top-4 text-gray-400"
                />

                <input
                  type="email"
                  placeholder="Enter email"
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-600 outline-none"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  required
                />

              </div>

            </div>

            <div>

              <label className="text-sm font-semibold">
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
                  placeholder="Create password"
                  className="w-full pl-12 pr-12 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-600 outline-none"
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  required
                />

                <button
                  type="button"
                  className="absolute right-4 top-3"
                  onClick={() =>
                    setShowPassword(!showPassword)
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

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 transition text-white py-3 rounded-xl flex justify-center items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2
                    className="animate-spin"
                    size={18}
                  />
                  Creating Account...
                </>
              ) : (
                "Create Free Account"
              )}
            </button>

            <p className="text-center text-slate-600">

              Already have an account?

              <Link
                to="/login"
                className="ml-2 text-blue-600 font-semibold hover:underline"
              >
                Login
              </Link>

            </p>

          </form>

        </div>

      </div>

    </div>
  );
}