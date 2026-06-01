import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export function AuthPage({ mode }: { mode: "login" | "signup" }) {
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setLoading(true);
    setError("");
    try {
      if (mode === "signup") {
        await signup(String(data.get("username")), String(data.get("email")), String(data.get("password")));
      } else {
        await login(String(data.get("username")), String(data.get("password")));
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 text-white">
      <form onSubmit={submit} className="glass w-full max-w-md rounded-lg p-6">
        <h1 className="text-3xl font-bold">{mode === "signup" ? "Create account" : "Welcome back"}</h1>
        <p className="mt-2 text-slate-300">Enter the interview workspace.</p>
        <label className="mt-6 block text-sm text-slate-300">Username</label>
        <input name="username" required className="focus-ring mt-2 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
        {mode === "signup" && (
          <>
            <label className="mt-4 block text-sm text-slate-300">Email</label>
            <input name="email" type="email" required className="focus-ring mt-2 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
          </>
        )}
        <label className="mt-4 block text-sm text-slate-300">Password</label>
        <input name="password" type="password" minLength={8} required className="focus-ring mt-2 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
        {error && <p className="mt-4 rounded-md bg-coral/15 p-3 text-sm text-coral">{error}</p>}
        <button disabled={loading} className="focus-ring mt-6 w-full rounded-md bg-mint px-4 py-3 font-semibold text-ink disabled:opacity-60">
          {loading ? "Working..." : mode === "signup" ? "Sign up" : "Log in"}
        </button>
        <p className="mt-4 text-center text-sm text-slate-300">
          {mode === "signup" ? "Already registered?" : "New here?"}{" "}
          <Link className="text-mint" to={mode === "signup" ? "/login" : "/signup"}>
            {mode === "signup" ? "Log in" : "Create account"}
          </Link>
        </p>
      </form>
    </main>
  );
}
