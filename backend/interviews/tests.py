from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import InterviewSession, JobDescription, Resume
from .services import skill_match_matrix


@override_settings(USE_SQLITE="1")
class InterviewFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="maya", email="maya@example.com", password="Password123!")
        self.client = APIClient()
        response = self.client.post("/api/auth/login/", {"username": "maya", "password": "Password123!"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_skill_match_matrix(self):
        resume = Resume.objects.create(
            user=self.user,
            file=SimpleUploadedFile("resume.txt", b"Python Django Docker"),
            raw_text="Python Django Docker",
            skills=["Python", "Django"],
        )
        jd = JobDescription.objects.create(
            user=self.user,
            title="Backend Engineer",
            raw_text="Need Python Django Docker",
            required_skills=["Python", "Django", "Docker"],
        )
        matrix = skill_match_matrix(resume, jd)
        self.assertEqual(matrix["Python"], 90)
        self.assertEqual(matrix["Docker"], 70)

    def test_create_session_generates_questions(self):
        resume = Resume.objects.create(
            user=self.user,
            file=SimpleUploadedFile("resume.txt", b"Python Django"),
            raw_text="Python Django",
            skills=["Python", "Django"],
        )
        jd = JobDescription.objects.create(
            user=self.user,
            title="Backend Engineer",
            raw_text="Need Python Django Docker",
            required_skills=["Python", "Django", "Docker"],
        )
        response = self.client.post("/api/sessions/", {"resume": resume.id, "job_description": jd.id}, format="json")
        self.assertEqual(response.status_code, 201)
        session = InterviewSession.objects.get(id=response.data["id"])
        self.assertEqual(session.status, InterviewSession.STATUS_IN_PROGRESS)
        self.assertGreaterEqual(session.questions.count(), 1)
