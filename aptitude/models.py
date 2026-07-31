from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    LEVEL = [('Basic', 'Basic'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    level = models.CharField(max_length=15, choices=LEVEL, default='Basic')
    concept = models.TextField(help_text="Concept explanation with formula")
    example = models.TextField(help_text="Worked example")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Problem(models.Model):
    DIFFICULTY = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    SOURCE = [('LeetCode', 'LeetCode'), ('GeeksforGeeks', 'GeeksforGeeks')]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='problems')
    question = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default='Medium')
    source = models.CharField(max_length=20, choices=SOURCE, default='GeeksforGeeks')
    link = models.URLField(max_length=400)
    answer_hint = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['topic__order', 'order']

    def __str__(self):
        return f"{self.question[:50]} [{self.topic.name}]"


class UserProblemProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apti_progress')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='progress')
    solved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'problem')
