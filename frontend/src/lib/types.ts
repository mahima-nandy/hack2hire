export type Resume = {
  id: number;
  file: string;
  raw_text: string;
  skills: string[];
  projects: string[];
  education: string[];
  experience: string[];
  created_at: string;
};

export type JobDescription = {
  id: number;
  title: string;
  raw_text: string;
  required_skills: string[];
  technologies: string[];
  experience_level: string;
  created_at: string;
};

export type Score = {
  accuracy: number;
  clarity: number;
  depth: number;
  relevance: number;
  communication: number;
  time_efficiency: number;
  overall: number;
  feedback: string;
  filler_words: Record<string, number>;
  repeated_words: Record<string, number>;
  excessive_pauses: number;
};

export type Answer = {
  id: number;
  question: number;
  transcript: string;
  response_time_seconds: number;
  late_submission: boolean;
  skipped: boolean;
  interviewer_response: string;
  score?: Score;
};

export type Question = {
  id: number;
  prompt: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  order: number;
  expected_topics: string[];
  time_limit_seconds: number;
  answer?: Answer;
};

export type Session = {
  id: number;
  resume: number;
  resume_detail: Resume;
  job_description: number;
  job_description_detail: JobDescription;
  status: string;
  current_difficulty: "easy" | "medium" | "hard";
  difficulty_progression: Array<{ score: number; next: string }>;
  skill_match: Record<string, number>;
  terminated_reason: string;
  questions: Question[];
  created_at: string;
};

export type Report = {
  id: number;
  session: number;
  overall_readiness_score: number;
  category: string;
  hiring_recommendation: string;
  reasoning: string;
  strengths: string[];
  weaknesses: string[];
  skill_gaps: string[];
  improvement_areas: string[];
  communication_score: number;
  technical_score: number;
  time_management_score: number;
  radar: Record<string, number>;
  created_at: string;
};
