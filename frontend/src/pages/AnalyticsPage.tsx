import { useEffect, useMemo, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";
import { StatCard } from "../components/Layout";
import { api } from "../lib/api";

type Summary = {
  session_count: number;
  completed_count: number;
  average_score: number;
  skill_history: Array<{ id: number; skill_match: Record<string, number> }>;
  difficulty_progression: Array<{ id: number; difficulty_progression: Array<{ score: number; next: string }> }>;
  interview_history: Array<{ id: number; status: string; question_count: number }>;
};

export function AnalyticsPage() {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api.analytics().then((data) => setSummary(data as Summary));
  }, []);

  const skills = useMemo(() => {
    const latest = summary?.skill_history?.[0]?.skill_match ?? {};
    return Object.entries(latest).map(([skill, score]) => ({ skill, score }));
  }, [summary]);

  const progression = useMemo(() => {
    const rows = summary?.difficulty_progression?.flatMap((session) =>
      session.difficulty_progression.map((item, index) => ({ question: index + 1, score: item.score, difficulty: item.next }))
    );
    return rows ?? [];
  }, [summary]);

  if (!summary) return <p className="text-slate-300">Loading analytics...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total interviews" value={summary.session_count} />
        <StatCard label="Completed" value={summary.completed_count} />
        <StatCard label="Average score" value={Math.round(summary.average_score)} tone="coral" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass rounded-lg p-5">
          <h2 className="text-xl font-semibold">Technical Skills</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer>
              <BarChart data={skills}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="skill" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#38f8b6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="glass rounded-lg p-5">
          <h2 className="text-xl font-semibold">Difficulty Progression</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer>
              <LineChart data={progression}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="question" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" domain={[0, 100]} />
                <Tooltip />
                <Line dataKey="score" stroke="#ff7a59" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}
