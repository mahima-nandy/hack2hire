from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Answer, InterviewSession, JobDescription, Question, Report, Resume, Score


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "file", "raw_text", "skills", "projects", "education", "experience", "created_at"]
        read_only_fields = ["raw_text", "skills", "projects", "education", "experience", "created_at"]


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ["id", "title", "file", "raw_text", "required_skills", "technologies", "experience_level", "created_at"]
        read_only_fields = ["required_skills", "technologies", "experience_level", "created_at"]
        extra_kwargs = {"raw_text": {"required": False, "allow_blank": True}}


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = [
            "accuracy",
            "clarity",
            "depth",
            "relevance",
            "communication",
            "time_efficiency",
            "overall",
            "feedback",
            "filler_words",
            "repeated_words",
            "excessive_pauses",
        ]


class AnswerSerializer(serializers.ModelSerializer):
    score = ScoreSerializer(read_only=True)
    audio = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "question",
            "transcript",
            "audio",
            "response_time_seconds",
            "late_submission",
            "skipped",
            "interviewer_response",
            "score",
            "created_at",
        ]
        read_only_fields = ["interviewer_response", "created_at"]

    def validate_question(self, question):
        request = self.context.get("request")
        if request and not request.user.is_staff and question.session.user != request.user:
            raise serializers.ValidationError("Question does not belong to the authenticated user.")
        return question


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ["id", "prompt", "category", "difficulty", "order", "expected_topics", "time_limit_seconds", "answer"]


class InterviewSessionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    resume_detail = ResumeSerializer(source="resume", read_only=True)
    job_description_detail = JobDescriptionSerializer(source="job_description", read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "resume",
            "resume_detail",
            "job_description",
            "job_description_detail",
            "status",
            "current_difficulty",
            "difficulty_progression",
            "skill_match",
            "terminated_reason",
            "started_at",
            "completed_at",
            "questions",
            "created_at",
        ]
        read_only_fields = [
            "status",
            "current_difficulty",
            "difficulty_progression",
            "skill_match",
            "terminated_reason",
            "started_at",
            "completed_at",
            "questions",
            "created_at",
        ]


class ReportSerializer(serializers.ModelSerializer):
    session_detail = InterviewSessionSerializer(source="session", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "session",
            "session_detail",
            "overall_readiness_score",
            "category",
            "hiring_recommendation",
            "reasoning",
            "strengths",
            "weaknesses",
            "skill_gaps",
            "improvement_areas",
            "communication_score",
            "technical_score",
            "time_management_score",
            "radar",
            "created_at",
        ]
