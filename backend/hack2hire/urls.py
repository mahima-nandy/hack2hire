from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from interviews.views import (
    AnswerViewSet,
    AdminUserViewSet,
    InterviewSessionViewSet,
    JobDescriptionViewSet,
    RegisterView,
    ReportViewSet,
    ResumeViewSet,
    analytics_summary,
)

router = DefaultRouter()
router.register("resumes", ResumeViewSet, basename="resume")
router.register("job-descriptions", JobDescriptionViewSet, basename="job-description")
router.register("sessions", InterviewSessionViewSet, basename="session")
router.register("answers", AnswerViewSet, basename="answer")
router.register("reports", ReportViewSet, basename="report")
router.register("admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/signup/", RegisterView.as_view(), name="signup"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/analytics/summary/", analytics_summary, name="analytics-summary"),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
