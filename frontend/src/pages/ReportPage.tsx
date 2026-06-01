import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from "recharts";
import { StatCard } from "../components/Layout";
import { api } from "../lib/api";
import { Report } from "../lib/types";

export function ReportsListPage() {
  const [reports, setReports] = useState<Report[]>([]);

  useEffect(() => {
    api.list<Report>("/reports").then(setReports);
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold">Reports</h1>
      <div className="mt-6 grid gap-4">
        {reports.map((report) => (
          <Link key={report.id} to={`/reports/${report.id}`} className="glass rounded-lg p-4 hover:border-mint/40">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold">Interview #{report.session}</p>
                <p className="text-slate-300">{report.category}</p>
              </div>
              <p className="text-3xl font-bold text-mint">{report.overall_readiness_score}/100</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export function ReportPage() {
  const { reportId } = useParams();
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    if (reportId) api.get<Report>("/reports", Number(reportId)).then(setReport);
  }, [reportId]);

  const radar = useMemo(
    () => Object.entries(report?.radar ?? {}).map(([metric, value]) => ({ metric, value })),
    [report]
  );

  if (!report) return <p className="text-slate-300">Loading report...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Hiring Readiness Report</h1>
        <p className="mt-2 text-slate-300">{report.reasoning}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Overall Score" value={`${report.overall_readiness_score}/100`} />
        <StatCard label="Technical" value={report.technical_score} />
        <StatCard label="Communication" value={report.communication_score} />
        <StatCard label="Time" value={report.time_management_score} tone="coral" />
      </div>
      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <section className="glass rounded-lg p-5">
          <h2 className="text-xl font-semibold">Readiness Indicator</h2>
          <p className="mt-4 text-5xl font-bold text-mint">{report.category}</p>
          <p className="mt-3 text-xl capitalize text-slate-200">{report.hiring_recommendation.replace("_", " ")}</p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <List title="Strengths" items={report.strengths} />
            <List title="Weaknesses" items={report.weaknesses} />
            <List title="Skill gaps" items={report.skill_gaps} />
            <List title="Improvement areas" items={report.improvement_areas} />
          </div>
        </section>
        <section className="glass rounded-lg p-5">
          <h2 className="text-xl font-semibold">Score Radar</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radar}>
                <PolarGrid stroke="rgba(255,255,255,0.2)" />
                <PolarAngleAxis dataKey="metric" stroke="#cbd5e1" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#94a3b8" />
                <Radar dataKey="value" stroke="#38f8b6" fill="#38f8b6" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg bg-white/5 p-4">
      <h3 className="font-semibold">{title}</h3>
      <ul className="mt-3 space-y-2 text-sm text-slate-300">
        {(items.length ? items : ["No major issues detected."]).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
