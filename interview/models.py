from django.db import models
from django.contrib.auth.models import User


class InterviewQuestion(models.Model):
    CATEGORY = [
        ('DSA', 'DSA'), ('OOP', 'OOP'), ('DBMS', 'DBMS'), ('OS', 'Operating Systems'),
        ('CN', 'Computer Networks'), ('SD', 'System Design'), ('HR', 'HR / Behavioral'),
        ('PROJ', 'Project / Resume'),
    ]
    SOURCE = [('LeetCode', 'LeetCode'), ('GeeksforGeeks', 'GeeksforGeeks')]

    rank = models.PositiveIntegerField()
    question = models.TextField()
    topic = models.CharField(max_length=60, default='Arrays', help_text="DSA pattern/topic this question belongs to")
    category = models.CharField(max_length=10, choices=CATEGORY, default='DSA')
    source = models.CharField(max_length=20, choices=SOURCE, default='GeeksforGeeks')
    link = models.URLField(max_length=400, blank=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} {self.question[:60]}"


class UserInterviewProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_progress')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='progress')
    marked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')
