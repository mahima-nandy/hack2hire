import { Link } from "react-router-dom";
import { ArrowRight, Brain, Mic, ShieldCheck } from "lucide-react";

export function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden text-white">
      <section className="mx-auto grid min-h-screen max-w-7xl items-center gap-10 px-4 py-12 lg:grid-cols-[1fr_0.9fr]">
        <div>
          <p className="mb-4 inline-flex rounded-md border border-mint/40 bg-mint/10 px-3 py-1 text-sm text-mint">
            Production-style AI technical interviews
          </p>
          <h1 className="max-w-4xl text-5xl font-bold leading-tight md:text-7xl">Hack2Hire AI Interview Platform</h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            Run adaptive voice-based mock interviews from a resume and job description, then get scored feedback, hiring readiness, and skill gap analytics.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="focus-ring inline-flex items-center gap-2 rounded-md bg-mint px-5 py-3 font-semibold text-ink" to="/signup">
              Start interview <ArrowRight size={18} />
            </Link>
            <Link className="focus-ring rounded-md border border-white/15 px-5 py-3 font-semibold text-white hover:bg-white/10" to="/login">
              Log in
            </Link>
          </div>
        </div>
        <div className="glass rounded-lg p-6">
          <div className="grid gap-4">
            {[
              { icon: Brain, title: "Adaptive engine", body: "Difficulty rises, falls, or holds based on answer quality." },
              { icon: Mic, title: "Voice workflow", body: "Record answers, transcribe with Whisper, and receive follow-ups." },
              { icon: ShieldCheck, title: "Hiring readiness", body: "Score accuracy, clarity, depth, relevance, communication, and time." }
            ].map((item) => (
              <div key={item.title} className="rounded-lg border border-white/10 bg-white/5 p-4">
                <item.icon className="text-mint" />
                <h2 className="mt-3 text-xl font-semibold">{item.title}</h2>
                <p className="mt-2 text-slate-300">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
