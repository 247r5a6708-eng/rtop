from django.db import models
from django.contrib.auth.models import User


class Pattern(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    DIFFICULTY = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    SOURCE = [('LeetCode', 'LeetCode'), ('GeeksforGeeks', 'GeeksforGeeks')]

    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default='Medium')
    source = models.CharField(max_length=20, choices=SOURCE, default='LeetCode')
    link = models.URLField(max_length=400)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['pattern__order', 'order']

    def __str__(self):
        return f"{self.title} [{self.pattern.name}]"


class UserQuestionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dsa_progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='progress')
    solved = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')
