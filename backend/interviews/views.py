from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, InterviewSession, JobDescription, Report, Resume
from .serializers import (
    AnswerSerializer,
    InterviewSessionSerializer,
    JobDescriptionSerializer,
    RegisterSerializer,
    ReportSerializer,
    ResumeSerializer,
    UserSerializer,
)
from .services import (
    analyze_job_description,
    analyze_resume,
    create_initial_questions,
    evaluate_answer,
    extract_text_from_upload,
    generate_follow_up,
    generate_report,
    skill_match_matrix,
    synthesize_speech,
    transcribe_audio,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(getattr(obj, "session", None), "user", None)
        return request.user.is_staff or owner == request.user


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_201_CREATED)


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = Resume.objects.all().order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)
        resume.raw_text = extract_text_from_upload(resume.file)
        resume.save(update_fields=["raw_text"])
        analyze_resume(resume)


class JobDescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = JobDescriptionSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = JobDescription.objects.all().order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        jd = serializer.save(user=self.request.user)
        if jd.file:
            jd.raw_text = f"{jd.raw_text}\n{extract_text_from_upload(jd.file)}".strip()
            jd.save(update_fields=["raw_text"])
        analyze_job_description(jd)


class InterviewSessionViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSessionSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = InterviewSession.objects.select_related("resume", "job_description", "user").prefetch_related("questions__answer__score").order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        session = serializer.save(user=self.request.user, status=InterviewSession.STATUS_IN_PROGRESS, started_at=timezone.now())
        session.skill_match = skill_match_matrix(session.resume, session.job_description)
        session.save(update_fields=["skill_match"])
        create_initial_questions(session)

    @action(detail=True, methods=["post"])
    def next_question(self, request, pk=None):
        session = self.get_object()
        unanswered = session.questions.filter(answer__isnull=True).order_by("order").first()
        if unanswered:
            return Response({"question_id": unanswered.id, "prompt": unanswered.prompt})
        last_answer = Answer.objects.filter(question__session=session).order_by("-question__order").first()
        if not last_answer:
            create_initial_questions(session, count=1)
            question = session.questions.order_by("-order").first()
        else:
            question = generate_follow_up(session, last_answer)
        return Response({"question_id": question.id, "prompt": question.prompt, "difficulty": question.difficulty})

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        session = self.get_object()
        report = generate_report(session)
        return Response(ReportSerializer(report).data)

    @action(detail=True, methods=["post"])
    def speak(self, request, pk=None):
        session = self.get_object()
        question = session.questions.filter(answer__isnull=True).order_by("order").first() or session.questions.order_by("-order").first()
        audio = synthesize_speech(question.prompt if question else "Welcome to your Hack2Hire interview.")
        return HttpResponse(audio, content_type="audio/mpeg")


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Answer.objects.select_related("question__session__user", "score").all().order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(question__session__user=self.request.user)

    def perform_create(self, serializer):
        transcript = serializer.validated_data.get("transcript", "")
        audio = serializer.validated_data.get("audio")
        if audio and not transcript:
            transcript = transcribe_audio(audio)
        answer = serializer.save(transcript=transcript)
        evaluate_answer(answer)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(self.get_serializer(self.get_queryset().get(pk=response.data["id"])).data, status=status.HTTP_201_CREATED)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Report.objects.select_related("session__user", "session__resume", "session__job_description").order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(session__user=self.request.user)


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("-date_joined")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_summary(request):
    sessions = InterviewSession.objects.filter(user=request.user)
    scores = Answer.objects.filter(question__session__user=request.user, score__isnull=False)
    return Response(
        {
            "session_count": sessions.count(),
            "completed_count": sessions.filter(status=InterviewSession.STATUS_COMPLETED).count(),
            "average_score": scores.aggregate(value=Avg("score__overall"))["value"] or 0,
            "skill_history": list(sessions.values("id", "skill_match", "created_at")[:10]),
            "difficulty_progression": list(sessions.values("id", "difficulty_progression")[:10]),
            "interview_history": list(sessions.values("id", "status", "created_at").annotate(question_count=Count("questions"))[:10]),
        }
    )
