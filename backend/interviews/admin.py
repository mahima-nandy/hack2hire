from django.contrib import admin

from .models import Answer, InterviewSession, JobDescription, Question, Report, Resume, Score


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username", "raw_text")


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "experience_level", "created_at")
    search_fields = ("title", "raw_text")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "current_difficulty", "created_at")
    list_filter = ("status", "current_difficulty")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "category", "difficulty", "order")
    list_filter = ("category", "difficulty")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "response_time_seconds", "late_submission", "skipped")


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "answer", "overall", "accuracy", "communication", "time_efficiency")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "overall_readiness_score", "hiring_recommendation", "category")
