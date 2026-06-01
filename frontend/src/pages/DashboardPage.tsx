import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud } from "lucide-react";
import { StatCard } from "../components/Layout";
import { api } from "../lib/api";
import { JobDescription, Resume, Session } from "../lib/types";

export function DashboardPage() {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const [resumeData, jdData, sessionData] = await Promise.all([
      api.list<Resume>("/resumes"),
      api.list<JobDescription>("/job-descriptions"),
      api.list<Session>("/sessions")
    ]);
    setResumes(resumeData);
    setJobs(jdData);
    setSessions(sessionData);
  }

  useEffect(() => {
    load();
  }, []);

  async function uploadResume(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.upload<Resume>("/resumes", form);
    setMessage("Resume analyzed successfully.");
    event.currentTarget.reset();
    load();
  }

  async function uploadJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.upload<JobDescription>("/job-descriptions", form);
    setMessage("Job description analyzed successfully.");
    event.currentTarget.reset();
    load();
  }

  async function startInterview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const session = await api.post<Session>("/sessions", {
      resume: Number(form.get("resume")),
      job_description: Number(form.get("job_description"))
    });
    navigate(`/interview/${session.id}`);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Interview Workspace</h1>
        <p className="mt-2 text-slate-300">Upload candidate context, compare it with the role, and start a live mock interview.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Resumes" value={resumes.length} />
        <StatCard label="Job Descriptions" value={jobs.length} />
        <StatCard label="Interviews" value={sessions.length} tone="coral" />
      </div>
      {message && <p className="rounded-md border border-mint/30 bg-mint/10 p-3 text-mint">{message}</p>}
      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={uploadResume} className="glass rounded-lg p-5">
          <UploadCloud className="text-mint" />
          <h2 className="mt-3 text-xl font-semibold">Resume Upload</h2>
          <input name="file" type="file" accept=".pdf,.txt" required className="mt-4 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
          <button className="mt-4 rounded-md bg-mint px-4 py-2 font-semibold text-ink">Analyze resume</button>
        </form>
        <form onSubmit={uploadJob} className="glass rounded-lg p-5">
          <h2 className="text-xl font-semibold">Job Description</h2>
          <input name="title" placeholder="Role title" required className="mt-4 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
          <textarea name="raw_text" placeholder="Paste JD text" required rows={5} className="mt-3 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
          <input name="file" type="file" accept=".pdf,.txt" className="mt-3 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3" />
          <button className="mt-4 rounded-md bg-mint px-4 py-2 font-semibold text-ink">Analyze JD</button>
        </form>
      </div>
      <form onSubmit={startInterview} className="glass rounded-lg p-5">
        <h2 className="text-xl font-semibold">Start Interview</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <select name="resume" required className="rounded-md border border-white/10 bg-ink px-3 py-3">
            <option value="">Select resume</option>
            {resumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                Resume #{resume.id} - {resume.skills.slice(0, 3).join(", ")}
              </option>
            ))}
          </select>
          <select name="job_description" required className="rounded-md border border-white/10 bg-ink px-3 py-3">
            <option value="">Select JD</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>
          <button className="rounded-md bg-coral px-5 py-3 font-semibold text-white">Begin</button>
        </div>
      </form>
    </div>
  );
}
