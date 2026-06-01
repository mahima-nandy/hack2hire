# Generated for Hack2Hire AI Interview Platform
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="JobDescription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("file", models.FileField(blank=True, null=True, upload_to="job_descriptions/")),
                ("raw_text", models.TextField()),
                ("required_skills", models.JSONField(default=list)),
                ("technologies", models.JSONField(default=list)),
                ("experience_level", models.CharField(blank=True, max_length=80)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="job_descriptions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Resume",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to="resumes/")),
                ("raw_text", models.TextField(blank=True)),
                ("skills", models.JSONField(default=list)),
                ("projects", models.JSONField(default=list)),
                ("education", models.JSONField(default=list)),
                ("experience", models.JSONField(default=list)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resumes", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="InterviewSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("created", "Created"), ("in_progress", "In Progress"), ("terminated", "Terminated"), ("completed", "Completed")], default="created", max_length=20)),
                ("current_difficulty", models.CharField(default="medium", max_length=20)),
                ("difficulty_progression", models.JSONField(default=list)),
                ("skill_match", models.JSONField(default=dict)),
                ("terminated_reason", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("job_description", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sessions", to="interviews.jobdescription")),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sessions", to="interviews.resume")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interview_sessions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("prompt", models.TextField()),
                ("category", models.CharField(choices=[("technical", "Technical"), ("behavioral", "Behavioral"), ("scenario", "Scenario-based"), ("problem_solving", "Problem solving")], max_length=40)),
                ("difficulty", models.CharField(choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")], max_length=20)),
                ("order", models.PositiveIntegerField()),
                ("expected_topics", models.JSONField(default=list)),
                ("time_limit_seconds", models.PositiveIntegerField(default=90)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="interviews.interviewsession")),
            ],
            options={"ordering": ["order"], "unique_together": {("session", "order")}},
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("transcript", models.TextField()),
                ("audio", models.FileField(blank=True, null=True, upload_to="answers/audio/")),
                ("response_time_seconds", models.PositiveIntegerField(default=0)),
                ("late_submission", models.BooleanField(default=False)),
                ("skipped", models.BooleanField(default=False)),
                ("interviewer_response", models.TextField(blank=True)),
                ("question", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="answer", to="interviews.question")),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("overall_readiness_score", models.PositiveSmallIntegerField(default=0)),
                ("category", models.CharField(max_length=80)),
                ("hiring_recommendation", models.CharField(choices=[("strong_hire", "Strong Hire"), ("hire", "Hire"), ("borderline", "Borderline"), ("reject", "Reject")], max_length=20)),
                ("reasoning", models.TextField()),
                ("strengths", models.JSONField(default=list)),
                ("weaknesses", models.JSONField(default=list)),
                ("skill_gaps", models.JSONField(default=list)),
                ("improvement_areas", models.JSONField(default=list)),
                ("communication_score", models.PositiveSmallIntegerField(default=0)),
                ("technical_score", models.PositiveSmallIntegerField(default=0)),
                ("time_management_score", models.PositiveSmallIntegerField(default=0)),
                ("radar", models.JSONField(default=dict)),
                ("session", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="report", to="interviews.interviewsession")),
            ],
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("accuracy", models.PositiveSmallIntegerField(default=0)),
                ("clarity", models.PositiveSmallIntegerField(default=0)),
                ("depth", models.PositiveSmallIntegerField(default=0)),
                ("relevance", models.PositiveSmallIntegerField(default=0)),
                ("communication", models.PositiveSmallIntegerField(default=0)),
                ("time_efficiency", models.PositiveSmallIntegerField(default=0)),
                ("overall", models.PositiveSmallIntegerField(default=0)),
                ("feedback", models.TextField(blank=True)),
                ("filler_words", models.JSONField(default=dict)),
                ("repeated_words", models.JSONField(default=dict)),
                ("excessive_pauses", models.PositiveIntegerField(default=0)),
                ("answer", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="score", to="interviews.answer")),
            ],
        ),
    ]
