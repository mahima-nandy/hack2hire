from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Resume(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/")
    raw_text = models.TextField(blank=True)
    skills = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    education = models.JSONField(default=list)
    experience = models.JSONField(default=list)

    def __str__(self):
        return f"Resume {self.id} for {self.user}"


class JobDescription(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_descriptions")
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="job_descriptions/", null=True, blank=True)
    raw_text = models.TextField()
    required_skills = models.JSONField(default=list)
    technologies = models.JSONField(default=list)
    experience_level = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.title


class InterviewSession(TimestampedModel):
    STATUS_CREATED = "created"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_TERMINATED = "terminated"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_TERMINATED, "Terminated"),
        (STATUS_COMPLETED, "Completed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_sessions")
    resume = models.ForeignKey(Resume, on_delete=models.PROTECT, related_name="sessions")
    job_description = models.ForeignKey(JobDescription, on_delete=models.PROTECT, related_name="sessions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    current_difficulty = models.CharField(max_length=20, default="medium")
    difficulty_progression = models.JSONField(default=list)
    skill_match = models.JSONField(default=dict)
    terminated_reason = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"InterviewSession {self.id}"


class Question(TimestampedModel):
    CATEGORY_CHOICES = [
        ("technical", "Technical"),
        ("behavioral", "Behavioral"),
        ("scenario", "Scenario-based"),
        ("problem_solving", "Problem solving"),
    ]
    DIFFICULTY_CHOICES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    order = models.PositiveIntegerField()
    expected_topics = models.JSONField(default=list)
    time_limit_seconds = models.PositiveIntegerField(default=90)

    class Meta:
        ordering = ["order"]
        unique_together = ("session", "order")

    def __str__(self):
        return self.prompt[:80]


class Answer(TimestampedModel):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="answer")
    transcript = models.TextField()
    audio = models.FileField(upload_to="answers/audio/", null=True, blank=True)
    response_time_seconds = models.PositiveIntegerField(default=0)
    late_submission = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    interviewer_response = models.TextField(blank=True)

    def __str__(self):
        return f"Answer to question {self.question_id}"


class Score(TimestampedModel):
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE, related_name="score")
    accuracy = models.PositiveSmallIntegerField(default=0)
    clarity = models.PositiveSmallIntegerField(default=0)
    depth = models.PositiveSmallIntegerField(default=0)
    relevance = models.PositiveSmallIntegerField(default=0)
    communication = models.PositiveSmallIntegerField(default=0)
    time_efficiency = models.PositiveSmallIntegerField(default=0)
    overall = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    filler_words = models.JSONField(default=dict)
    repeated_words = models.JSONField(default=dict)
    excessive_pauses = models.PositiveIntegerField(default=0)

    def metric_values(self):
        return [
            self.accuracy,
            self.clarity,
            self.depth,
            self.relevance,
            self.communication,
            self.time_efficiency,
        ]


class Report(TimestampedModel):
    RECOMMENDATION_CHOICES = [
        ("strong_hire", "Strong Hire"),
        ("hire", "Hire"),
        ("borderline", "Borderline"),
        ("reject", "Reject"),
    ]
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name="report")
    overall_readiness_score = models.PositiveSmallIntegerField(default=0)
    category = models.CharField(max_length=80)
    hiring_recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES)
    reasoning = models.TextField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    improvement_areas = models.JSONField(default=list)
    communication_score = models.PositiveSmallIntegerField(default=0)
    technical_score = models.PositiveSmallIntegerField(default=0)
    time_management_score = models.PositiveSmallIntegerField(default=0)
    radar = models.JSONField(default=dict)

    def __str__(self):
        return f"Report {self.id} for session {self.session_id}"
