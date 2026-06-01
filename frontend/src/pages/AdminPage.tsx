import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { api } from "../lib/api";
import { Report, Session } from "../lib/types";

type AdminUser = {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  date_joined: string;
};

export function AdminPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [adminNotice, setAdminNotice] = useState("");

  async function load() {
    const [sessionData, reportData] = await Promise.all([api.list<Session>("/sessions"), api.list<Report>("/reports")]);
    setSessions(sessionData);
    setReports(reportData);
    try {
      setUsers(await api.list<AdminUser>("/admin/users"));
      setAdminNotice("");
    } catch {
      setAdminNotice("User management is visible to staff accounts only.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function removeSession(id: number) {
    await fetch(`${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api"}/sessions/${id}/`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` }
    });
    load();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Admin Dashboard</h1>
      {adminNotice && <p className="rounded-md border border-coral/30 bg-coral/10 p-3 text-coral">{adminNotice}</p>}
      <section className="glass rounded-lg p-5">
        <h2 className="text-xl font-semibold">Users</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {users.map((user) => (
            <div key={user.id} className="rounded-lg bg-white/5 p-4">
              <p className="font-semibold">{user.username}</p>
              <p className="text-sm text-slate-300">{user.email || "No email"}</p>
              <p className="mt-2 text-sm text-mint">{user.is_staff ? "Staff" : "Candidate"}</p>
            </div>
          ))}
        </div>
      </section>
      <section className="glass rounded-lg p-5">
        <h2 className="text-xl font-semibold">Interviews</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[620px] text-left text-sm">
            <thead className="text-slate-400">
              <tr>
                <th className="py-2">ID</th>
                <th>Status</th>
                <th>Difficulty</th>
                <th>Questions</th>
                <th>Skill Match</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id} className="border-t border-white/10">
                  <td className="py-3">{session.id}</td>
                  <td>{session.status}</td>
                  <td>{session.current_difficulty}</td>
                  <td>{session.questions.length}</td>
                  <td>{Object.keys(session.skill_match).slice(0, 3).join(", ")}</td>
                  <td>
                    <button onClick={() => removeSession(session.id)} className="rounded-md border border-white/10 p-2 hover:bg-white/10" aria-label="Delete session">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="glass rounded-lg p-5">
        <h2 className="text-xl font-semibold">Reports</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {reports.map((report) => (
            <div key={report.id} className="rounded-lg bg-white/5 p-4">
              <p className="font-semibold">Report #{report.id}</p>
              <p className="text-slate-300">{report.category}</p>
              <p className="mt-2 text-2xl font-bold text-mint">{report.overall_readiness_score}/100</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
