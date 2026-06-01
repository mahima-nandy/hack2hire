import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, FileText, Home, LogOut, Shield, Video } from "lucide-react";
import { useAuth } from "../lib/auth";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: Home },
  { to: "/interview", label: "Interview", icon: Video },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/admin", label: "Admin", icon: Shield },
  { to: "/analytics", label: "Analytics", icon: BarChart3 }
];

export function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen text-white">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-ink/75 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/dashboard" className="text-lg font-bold tracking-wide">
            Hack2Hire
          </Link>
          <nav className="hidden items-center gap-2 md:flex">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-md px-3 py-2 text-sm transition ${
                    isActive ? "bg-mint text-ink" : "text-slate-300 hover:bg-white/10"
                  }`
                }
              >
                <item.icon size={16} />
                {item.label}
              </NavLink>
            ))}
          </nav>
          <button
            className="focus-ring rounded-md border border-white/10 p-2 text-slate-200 hover:bg-white/10"
            onClick={() => {
              logout();
              navigate("/");
            }}
            aria-label="Log out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}

export function StatCard({ label, value, tone = "mint" }: { label: string; value: string | number; tone?: "mint" | "coral" }) {
  return (
    <div className="glass rounded-lg p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${tone === "mint" ? "text-mint" : "text-coral"}`}>{value}</p>
    </div>
  );
}
