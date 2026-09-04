import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  Mail,
  ArrowLeft,
  Loader2,
  ShieldCheck,
} from "lucide-react";

import api from "../../api/axios";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post(
        "/auth/forgot-password",
        { email }
      );

      setMessage(response.data.message);

    } catch (err) {

      setError(
        err.response?.data?.detail ||
        "Unable to send reset link."
      );

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="min-h-screen flex bg-slate-100">

      {/* Left Section */}

      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-blue-700 via-blue-600 to-indigo-700 text-white p-16 flex-col justify-center">

        <div className="flex items-center gap-4">

          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">

            <Sparkles size={34} />

          </div>

          <div>

            <h1 className="text-4xl font-bold">
              ViralForge AI
            </h1>

            <p className="text-blue-100 mt-2">
              AI Powered Content Automation
            </p>

          </div>

        </div>

        <div className="mt-16 space-y-8">

          <div className="flex gap-4">

            <ShieldCheck size={34} />

            <div>

              <h3 className="text-xl font-semibold">
                Secure Account Recovery
              </h3>

              <p className="text-blue-100 mt-2">
                Recover your account safely using your registered email.
              </p>

            </div>

          </div>

          <div className="flex gap-4">

            <Mail size={34} />

            <div>

              <h3 className="text-xl font-semibold">
                Instant Reset Link
              </h3>

              <p className="text-blue-100 mt-2">
                We'll send a password reset link directly to your inbox.
              </p>

            </div>

          </div>

        </div>

      </div>

      {/* Right Section */}

      <div className="flex flex-1 items-center justify-center p-4 sm:p-8">

        <div className="w-full max-w-md rounded-3xl bg-white p-5 shadow-2xl sm:p-10">

          <div className="text-center mb-8">

            <div className="w-16 h-16 rounded-2xl bg-blue-100 mx-auto flex items-center justify-center">

              <Mail className="text-blue-600" size={30} />

            </div>

            <h2 className="text-3xl font-bold mt-6">
              Forgot Password
            </h2>

            <p className="text-slate-500 mt-2">
              Enter your registered email address.
            </p>

          </div>

          {message && (

            <div className="mb-5 bg-green-100 text-green-700 p-4 rounded-xl">

              {message}

            </div>

          )}

          {error && (

            <div className="mb-5 bg-red-100 text-red-700 p-4 rounded-xl">

              {error}

            </div>

          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >

            <div>

              <label className="block mb-2 font-medium">

                Email Address

              </label>

              <div className="relative">

                <Mail
                  className="absolute left-4 top-4 text-slate-400"
                  size={20}
                />

                <input
                  type="email"
                  value={email}
                  onChange={(e)=>setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full border rounded-xl pl-12 pr-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />

              </div>

            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 transition text-white font-semibold py-3 rounded-xl flex justify-center items-center gap-2"
            >

              {loading ? (
                <>
                  <Loader2
                    className="animate-spin"
                    size={18}
                  />
                  Sending...
                </>
              ) : (
                "Send Reset Link"
              )}

            </button>

          </form>

          <div className="mt-8 text-center">

            <Link
              to="/login"
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >

              <ArrowLeft size={18} />

              Back to Login

            </Link>

          </div>

        </div>

      </div>

    </div>
  );
}
