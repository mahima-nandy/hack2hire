import json
import re
from collections import Counter
from statistics import mean

from django.conf import settings
from django.utils import timezone
from openai import OpenAI
from pypdf import PdfReader

from .models import Answer, InterviewSession, JobDescription, Question, Report, Resume, Score

SKILL_BANK = [
    "Python",
    "Django",
    "React",
    "TypeScript",
    "JavaScript",
    "PostgreSQL",
    "Docker",
    "REST",
    "WebSocket",
    "AWS",
    "Kubernetes",
    "Redis",
    "CI/CD",
    "SQL",
    "System Design",
    "Testing",
    "Machine Learning",
    "OpenAI",
]

FILLERS = {"um", "uh", "like", "basically", "actually", "literally", "you know", "sort of", "kind of"}
DIFFICULTIES = ["easy", "medium", "hard"]


def clamp(value):
    return max(0, min(100, int(round(value))))


def openai_client():
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_pdf_text(file_obj):
    file_obj.seek(0)
    reader = PdfReader(file_obj)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def extract_text_from_upload(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_pdf_text(uploaded_file)
    return uploaded_file.read().decode("utf-8", errors="ignore")


def _json_chat(system, user, fallback):
    client = openai_client()
    if not client:
        return fallback()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


def detect_skills(text):
    found = []
    lower = text.lower()
    for skill in SKILL_BANK:
        if skill.lower() in lower:
            found.append(skill)
    return sorted(set(found))


def extract_sections(text, markers):
    results = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if any(marker in line.lower() for marker in markers):
            results.append(line[:220])
    return results[:8]


def analyze_resume(resume: Resume):
    text = resume.raw_text

    def fallback():
        return {
            "skills": detect_skills(text),
            "projects": extract_sections(text, ["project", "built", "implemented"]),
            "education": extract_sections(text, ["university", "college", "degree", "b.tech", "bachelor", "master"]),
            "experience": extract_sections(text, ["experience", "engineer", "developer", "intern", "company"]),
        }

    data = _json_chat(
        "Extract structured candidate resume data. Return JSON keys: skills, projects, education, experience. Values must be arrays.",
        text[:12000],
        fallback,
    )
    resume.skills = data.get("skills", [])
    resume.projects = data.get("projects", [])
    resume.education = data.get("education", [])
    resume.experience = data.get("experience", [])
    resume.save(update_fields=["skills", "projects", "education", "experience", "updated_at"])
    return resume


def analyze_job_description(jd: JobDescription):
    text = jd.raw_text

    def fallback():
        skills = detect_skills(text)
        seniority = "senior" if re.search(r"\b(5\+|senior|lead|staff)\b", text, re.I) else "mid-level"
        if re.search(r"\b(intern|entry|junior|0-2)\b", text, re.I):
            seniority = "entry-level"
        return {"required_skills": skills, "technologies": skills, "experience_level": seniority}

    data = _json_chat(
        "Extract a job description. Return JSON keys: required_skills, technologies, experience_level.",
        text[:12000],
        fallback,
    )
    jd.required_skills = data.get("required_skills", [])
    jd.technologies = data.get("technologies", [])
    jd.experience_level = data.get("experience_level", "")
    jd.save(update_fields=["required_skills", "technologies", "experience_level", "updated_at"])
    return jd


def skill_match_matrix(resume: Resume, jd: JobDescription):
    resume_text = " ".join(resume.skills).lower() + " " + resume.raw_text.lower()
    required = jd.required_skills or jd.technologies or detect_skills(jd.raw_text)
    matrix = {}
    for skill in required:
        name = str(skill).strip()
        if not name:
            continue
        exact = name.lower() in [s.lower() for s in resume.skills]
        mentioned = name.lower() in resume_text
        matrix[name] = 90 if exact else 70 if mentioned else 35
    return matrix


def create_initial_questions(session: InterviewSession, count=6):
    gaps = [skill for skill, score in session.skill_match.items() if score < 70]
    skills = list(session.skill_match.keys())[:6]

    def fallback():
        focus = gaps or skills or ["software engineering"]
        categories = ["technical", "behavioral", "scenario", "problem_solving", "technical", "scenario"]
        return {
            "questions": [
                {
                    "prompt": f"Walk me through your experience with {focus[i % len(focus)]} and one trade-off you handled.",
                    "category": categories[i % len(categories)],
                    "difficulty": "medium" if i < 3 else "hard",
                    "expected_topics": [focus[i % len(focus)], "trade-offs", "practical example"],
                }
                for i in range(count)
            ]
        }

    data = _json_chat(
        "Generate interview questions from resume/JD/skill gaps. Return JSON key questions as array with prompt, category, difficulty, expected_topics.",
        json.dumps(
            {
                "resume_skills": session.resume.skills,
                "projects": session.resume.projects,
                "job_skills": session.job_description.required_skills,
                "skill_gaps": gaps,
                "current_difficulty": session.current_difficulty,
            }
        ),
        fallback,
    )
    created = []
    for index, item in enumerate(data.get("questions", [])[:count], start=1):
        created.append(
            Question.objects.create(
                session=session,
                prompt=item.get("prompt", "Describe a relevant technical challenge you solved."),
                category=item.get("category", "technical"),
                difficulty=item.get("difficulty", session.current_difficulty),
                expected_topics=item.get("expected_topics", []),
                order=index,
            )
        )
    return created


def transcribe_audio(file_obj):
    client = openai_client()
    if not client:
        return ""
    file_obj.seek(0)
    transcript = client.audio.transcriptions.create(model=settings.OPENAI_STT_MODEL, file=file_obj)
    return transcript.text


def synthesize_speech(text):
    client = openai_client()
    if not client:
        return b""
    response = client.audio.speech.create(model=settings.OPENAI_TTS_MODEL, voice="alloy", input=text)
    return response.read()


def communication_analysis(transcript):
    lower = transcript.lower()
    words = re.findall(r"[a-zA-Z']+", lower)
    filler_counts = {word: lower.count(word) for word in FILLERS if word in lower}
    repeated = {word: count for word, count in Counter(words).items() if count >= 4 and len(word) > 3}
    pauses = len(re.findall(r"\.{3,}|\[pause\]|\(pause\)", lower))
    communication_score = 100 - (sum(filler_counts.values()) * 4) - (len(repeated) * 3) - (pauses * 8)
    return filler_counts, repeated, pauses, clamp(communication_score)


def evaluate_answer(answer: Answer):
    question = answer.question
    transcript = answer.transcript or ""
    filler_counts, repeated, pauses, communication_score = communication_analysis(transcript)
    time_score = 100 if answer.response_time_seconds <= question.time_limit_seconds else 70
    if answer.late_submission:
        time_score -= 20
    if answer.skipped:
        time_score = 0

    def fallback():
        word_count = len(transcript.split())
        expected_hits = sum(1 for topic in question.expected_topics if str(topic).lower() in transcript.lower())
        base = min(85, 35 + word_count * 2 + expected_hits * 12)
        if answer.skipped or word_count < 8:
            base = 20
        return {
            "accuracy": base,
            "clarity": min(base + 5, 90),
            "depth": min(base + (10 if word_count > 55 else 0), 92),
            "relevance": min(base + expected_hits * 5, 95),
            "feedback": "Answer was evaluated for topical coverage, structure, relevance, and delivery.",
            "interviewer_response": "Can you expand on the key trade-off and explain how you measured success?",
        }

    data = _json_chat(
        "Evaluate an interview answer. Return JSON keys accuracy, clarity, depth, relevance, feedback, interviewer_response. Scores are 0-100.",
        json.dumps({"question": question.prompt, "expected_topics": question.expected_topics, "answer": transcript}),
        fallback,
    )
    values = {
        "accuracy": clamp(data.get("accuracy", 0)),
        "clarity": clamp(data.get("clarity", 0)),
        "depth": clamp(data.get("depth", 0)),
        "relevance": clamp(data.get("relevance", 0)),
        "communication": communication_score,
        "time_efficiency": clamp(time_score),
    }
    overall = clamp(mean(values.values()))
    score, _ = Score.objects.update_or_create(
        answer=answer,
        defaults={
            **values,
            "overall": overall,
            "feedback": data.get("feedback", ""),
            "filler_words": filler_counts,
            "repeated_words": repeated,
            "excessive_pauses": pauses,
        },
    )
    answer.interviewer_response = data.get("interviewer_response", "")
    answer.save(update_fields=["interviewer_response", "updated_at"])
    update_session_after_score(question.session, overall)
    return score


def update_session_after_score(session: InterviewSession, score):
    current = session.current_difficulty
    idx = DIFFICULTIES.index(current)
    if score > 80:
        idx = min(idx + 1, len(DIFFICULTIES) - 1)
    elif score < 50:
        idx = max(idx - 1, 0)
    session.current_difficulty = DIFFICULTIES[idx]
    session.difficulty_progression = [*session.difficulty_progression, {"score": score, "next": session.current_difficulty}]

    first_five = Score.objects.filter(answer__question__session=session).order_by("answer__question__order")[:5]
    if len(first_five) == 5 and mean([item.overall for item in first_five]) < 30:
        session.status = InterviewSession.STATUS_TERMINATED
        session.terminated_reason = "Interview terminated due to low performance threshold."
        session.completed_at = timezone.now()
    session.save(update_fields=["current_difficulty", "difficulty_progression", "status", "terminated_reason", "completed_at", "updated_at"])


def generate_follow_up(session: InterviewSession, previous_answer: Answer):
    next_order = session.questions.count() + 1
    prompt = previous_answer.interviewer_response or "Can you go deeper and provide a concrete production example?"
    return Question.objects.create(
        session=session,
        prompt=prompt,
        category="technical",
        difficulty=session.current_difficulty,
        order=next_order,
        expected_topics=["example", "trade-off", "impact"],
    )


def generate_report(session: InterviewSession):
    scores = list(Score.objects.filter(answer__question__session=session))
    if not scores:
        raise ValueError("Cannot generate a report before answers are scored.")
    overall = clamp(mean([score.overall for score in scores]))
    technical = clamp(mean([mean([score.accuracy, score.depth, score.relevance]) for score in scores]))
    communication = clamp(mean([score.communication for score in scores]))
    time_management = clamp(mean([score.time_efficiency for score in scores]))
    gaps = [skill for skill, value in session.skill_match.items() if value < 70]
    if overall >= 85:
        category, recommendation = "Strong Candidate", "strong_hire"
    elif overall >= 70:
        category, recommendation = "Ready Candidate", "hire"
    elif overall >= 50:
        category, recommendation = "Borderline Candidate", "borderline"
    else:
        category, recommendation = "Needs Significant Improvement", "reject"
    report, _ = Report.objects.update_or_create(
        session=session,
        defaults={
            "overall_readiness_score": overall,
            "category": category,
            "hiring_recommendation": recommendation,
            "reasoning": f"Recommendation is based on technical score {technical}, communication score {communication}, and time management score {time_management}.",
            "strengths": ["Relevant project experience", "Structured technical reasoning"] if technical >= 70 else ["Completed the interview flow"],
            "weaknesses": ["Needs deeper examples for weaker skills"] if gaps else ["Maintain consistency under time pressure"],
            "skill_gaps": gaps,
            "improvement_areas": ["Practice concise STAR responses", "Review lower-matched JD skills", "Use concrete metrics in answers"],
            "communication_score": communication,
            "technical_score": technical,
            "time_management_score": time_management,
            "radar": {
                "accuracy": clamp(mean([s.accuracy for s in scores])),
                "clarity": clamp(mean([s.clarity for s in scores])),
                "depth": clamp(mean([s.depth for s in scores])),
                "relevance": clamp(mean([s.relevance for s in scores])),
                "communication": communication,
                "time": time_management,
            },
        },
    )
    session.status = InterviewSession.STATUS_COMPLETED if session.status != InterviewSession.STATUS_TERMINATED else session.status
    session.completed_at = timezone.now()
    session.save(update_fields=["status", "completed_at", "updated_at"])
    return report
