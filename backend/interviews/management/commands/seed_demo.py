from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from interviews.models import Answer, InterviewSession, JobDescription, Question, Resume
from interviews.services import evaluate_answer, generate_report, skill_match_matrix


RESUME_TEXT = """Aarav Sharma
Backend Engineer

Skills: Python, Django, REST, PostgreSQL, Docker, React, TypeScript, WebSocket, Testing, OpenAI

Experience:
- Built Django REST APIs for a hiring analytics platform with PostgreSQL and Docker.
- Implemented WebSocket notifications and JWT authentication for production workflows.

Projects:
- AI mock interview assistant using resume parsing, adaptive question generation, and scoring.
- Candidate dashboard with React, TypeScript, charts, and role-based access.

Education:
- B.Tech Computer Science, National Institute of Technology
"""

JD_TEXT = """Senior Full Stack Engineer

We need a full-stack engineer with Python, Django, Django REST Framework, PostgreSQL, Docker,
React, TypeScript, WebSocket experience, testing discipline, and practical AI integration.
The role requires building secure APIs, analytics dashboards, and production-ready user flows.
"""

ANSWERS = [
    "I built Django REST APIs with serializers, permissions, JWT authentication, and PostgreSQL models. I focused on clean ownership boundaries, migrations, and tests for critical API behavior.",
    "For Docker I use separate backend and frontend images, environment-based configuration, and compose services for the database, API, and web UI. I also keep secrets out of source control.",
    "A WebSocket is useful for low-latency interview room updates such as timer events, transcript status, and interviewer responses. REST still handles durable records like answers and reports.",
    "When an answer is weak, an adaptive engine should lower difficulty to recover signal. When a candidate scores high, it should increase depth and ask more scenario-based follow-ups.",
    "I would measure success with response latency, completion rate, report quality, score consistency, and candidate feedback. I would also monitor transcription failures and API costs.",
    "For communication I try to give a short summary, then the technical details, then impact. That keeps the answer clear while still showing depth.",
]


class Command(BaseCommand):
    help = "Create demo accounts, sample resume/JD, interview session, answers, scores, and report."

    def handle(self, *args, **options):
        demo_user, _ = User.objects.update_or_create(
            username="demo",
            defaults={"email": "demo@hack2hire.local", "is_staff": False},
        )
        demo_user.set_password("DemoPass123!")
        demo_user.save()

        admin_user, _ = User.objects.update_or_create(
            username="admin",
            defaults={"email": "admin@hack2hire.local", "is_staff": True, "is_superuser": True},
        )
        admin_user.set_password("AdminPass123!")
        admin_user.save()

        InterviewSession.objects.filter(user=demo_user).delete()
        Resume.objects.filter(user=demo_user).delete()
        JobDescription.objects.filter(user=demo_user).delete()

        resume = Resume.objects.create(
            user=demo_user,
            file=ContentFile(RESUME_TEXT.encode("utf-8"), name="sample_resume.txt"),
            raw_text=RESUME_TEXT,
            skills=["Python", "Django", "REST", "PostgreSQL", "Docker", "React", "TypeScript", "WebSocket", "Testing", "OpenAI"],
            projects=["AI mock interview assistant", "Candidate analytics dashboard"],
            education=["B.Tech Computer Science, National Institute of Technology"],
            experience=["Backend Engineer building Django APIs, WebSockets, JWT auth, and Dockerized workflows"],
        )
        jd = JobDescription.objects.create(
            user=demo_user,
            title="Senior Full Stack Engineer",
            file=ContentFile(JD_TEXT.encode("utf-8"), name="sample_jd.txt"),
            raw_text=JD_TEXT,
            required_skills=["Python", "Django", "PostgreSQL", "Docker", "React", "TypeScript", "WebSocket", "Testing", "AI integration"],
            technologies=["Python", "Django", "DRF", "PostgreSQL", "Docker", "React", "TypeScript", "WebSocket"],
            experience_level="senior",
        )
        session = InterviewSession.objects.create(
            user=demo_user,
            resume=resume,
            job_description=jd,
            status=InterviewSession.STATUS_IN_PROGRESS,
            current_difficulty="medium",
            skill_match=skill_match_matrix(resume, jd),
            started_at=timezone.now(),
        )
        prompts = [
            ("Explain how you structure a production Django REST API.", "technical", "medium"),
            ("How would you containerize this platform for a hackathon demo?", "scenario", "medium"),
            ("When would you choose WebSockets instead of REST?", "technical", "medium"),
            ("Describe the adaptive difficulty logic you would use.", "problem_solving", "hard"),
            ("How would you measure whether this platform is useful?", "behavioral", "hard"),
            ("Give an example of communicating a complex backend decision clearly.", "behavioral", "medium"),
        ]
        for index, (prompt, category, difficulty) in enumerate(prompts, start=1):
            question = Question.objects.create(
                session=session,
                prompt=prompt,
                category=category,
                difficulty=difficulty,
                order=index,
                expected_topics=["Django", "production", "trade-off"],
            )
            answer = Answer.objects.create(
                question=question,
                transcript=ANSWERS[index - 1],
                response_time_seconds=55 + index * 4,
                late_submission=False,
                skipped=False,
            )
            evaluate_answer(answer)
        report = generate_report(session)
        self.stdout.write(self.style.SUCCESS("Demo data created."))
        self.stdout.write("Candidate: demo / DemoPass123!")
        self.stdout.write("Admin: admin / AdminPass123!")
        self.stdout.write(f"Session ID: {session.id}")
        self.stdout.write(f"Report ID: {report.id}")
