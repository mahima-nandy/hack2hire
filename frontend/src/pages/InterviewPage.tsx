import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Mic, Pause, Send, SkipForward, Volume2 } from "lucide-react";
import { api, tokenStore, websocketUrl } from "../lib/api";
import { Answer, Question, Session } from "../lib/types";

export function InterviewPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [current, setCurrent] = useState<Question | null>(null);
  const [seconds, setSeconds] = useState(90);
  const [transcript, setTranscript] = useState("");
  const [recording, setRecording] = useState(false);
  const [audio, setAudio] = useState<Blob | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<BlobPart[]>([]);

  async function load() {
    if (!sessionId) return;
    const data = await api.get<Session>("/sessions", Number(sessionId));
    setSession(data);
    const next = data.questions.find((question) => !question.answer) ?? data.questions[data.questions.length - 1] ?? null;
    setCurrent(next);
    setSeconds(next?.time_limit_seconds ?? 90);
  }

  useEffect(() => {
    load();
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    const ws = new WebSocket(websocketUrl(Number(sessionId)));
    ws.onmessage = () => undefined;
    return () => ws.close();
  }, [sessionId]);

  useEffect(() => {
    if (!current || session?.status === "terminated") return;
    const timer = window.setInterval(() => setSeconds((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [current, session?.status]);

  const timeLabel = useMemo(() => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`, [seconds]);

  async function toggleRecording() {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    chunks.current = [];
    mediaRecorder.ondataavailable = (event) => chunks.current.push(event.data);
    mediaRecorder.onstop = () => {
      setAudio(new Blob(chunks.current, { type: "audio/webm" }));
      stream.getTracks().forEach((track) => track.stop());
    };
    recorder.current = mediaRecorder;
    mediaRecorder.start();
    setRecording(true);
  }

  async function submit(skipped = false) {
    if (!current) return;
    const form = new FormData();
    form.set("question", String(current.id));
    form.set("transcript", skipped ? "Skipped answer." : transcript);
    form.set("response_time_seconds", String(current.time_limit_seconds - seconds));
    form.set("late_submission", String(seconds === 0));
    form.set("skipped", String(skipped));
    if (audio) form.set("audio", audio, "answer.webm");
    const answer = await api.answer<Answer>(form);
    setTranscript(answer.interviewer_response);
    if (sessionId) {
      const updated = await api.get<Session>("/sessions", Number(sessionId));
      setSession(updated);
      if (updated.status === "terminated") return;
      const response = await api.action<{ question_id: number }>("/sessions", Number(sessionId), "next_question");
      const reloaded = await api.get<Session>("/sessions", Number(sessionId));
      setSession(reloaded);
      const next = reloaded.questions.find((question) => question.id === response.question_id) ?? null;
      setCurrent(next);
      setSeconds(next?.time_limit_seconds ?? 90);
      setAudio(null);
      setTranscript("");
    }
  }

  async function finish() {
    if (!sessionId) return;
    const report = await api.action<{ id: number }>("/sessions", Number(sessionId), "finish");
    navigate(`/reports/${report.id}`);
  }

  async function speakQuestion() {
    if (!sessionId) return;
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api"}/sessions/${sessionId}/speak/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${tokenStore.access}` }
    });
    const blob = await response.blob();
    if (blob.size > 0) new Audio(URL.createObjectURL(blob)).play();
  }

  if (!sessionId) {
    return <p className="text-slate-300">Choose or start an interview from the dashboard.</p>;
  }

  if (!session || !current) {
    return <p className="text-slate-300">Loading interview room...</p>;
  }

  if (session.status === "terminated") {
    return (
      <div className="glass rounded-lg p-6">
        <h1 className="text-3xl font-bold text-coral">Interview terminated</h1>
        <p className="mt-3 text-slate-200">{session.terminated_reason}</p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <section className="glass rounded-lg p-5">
        <div className="mx-auto grid h-44 w-44 place-items-center rounded-full border border-mint/40 bg-mint/10 text-6xl">AI</div>
        <div className="mt-5 grid grid-cols-2 gap-3 text-center">
          <div className="rounded-lg bg-white/5 p-3">
            <p className="text-sm text-slate-400">Timer</p>
            <p className={`text-3xl font-bold ${seconds < 15 ? "text-coral" : "text-mint"}`}>{timeLabel}</p>
          </div>
          <div className="rounded-lg bg-white/5 p-3">
            <p className="text-sm text-slate-400">Difficulty</p>
            <p className="text-3xl font-bold capitalize">{current.difficulty}</p>
          </div>
        </div>
        <button onClick={finish} className="mt-5 w-full rounded-md border border-white/15 px-4 py-3 hover:bg-white/10">
          Finish and generate report
        </button>
      </section>
      <section className="glass rounded-lg p-5">
        <p className="text-sm uppercase tracking-[0.2em] text-mint">{current.category}</p>
        <h1 className="mt-3 text-2xl font-semibold leading-snug">{current.prompt}</h1>
        <button onClick={speakQuestion} className="mt-4 inline-flex items-center gap-2 rounded-md border border-white/15 px-3 py-2 text-sm hover:bg-white/10">
          <Volume2 size={16} />
          Play question
        </button>
        <textarea
          value={transcript}
          onChange={(event) => setTranscript(event.target.value)}
          rows={8}
          className="mt-5 w-full rounded-md border border-white/10 bg-white/10 px-3 py-3"
          placeholder="Your transcript appears here. You can also type or edit before submitting."
        />
        <div className="mt-4 flex flex-wrap gap-3">
          <button onClick={toggleRecording} className="inline-flex items-center gap-2 rounded-md bg-mint px-4 py-3 font-semibold text-ink">
            {recording ? <Pause size={18} /> : <Mic size={18} />}
            {recording ? "Stop" : "Record"}
          </button>
          <button onClick={() => submit(false)} className="inline-flex items-center gap-2 rounded-md bg-coral px-4 py-3 font-semibold text-white">
            <Send size={18} />
            Submit answer
          </button>
          <button onClick={() => submit(true)} className="inline-flex items-center gap-2 rounded-md border border-white/15 px-4 py-3">
            <SkipForward size={18} />
            Skip
          </button>
        </div>
        {recording && <p className="mt-3 text-mint">Recording in progress...</p>}
      </section>
    </div>
  );
}
