from django.db import models
from django.contrib.auth.models import User


class Concept(models.Model):
    DOMAIN = [
        ('OOP', 'Object Oriented Programming'), ('DBMS', 'DBMS'), ('OS', 'Operating Systems'),
        ('CN', 'Computer Networks'), ('SE', 'Software Engineering'), ('SD', 'System Design'),
    ]
    LEVEL = [('Basic', 'Basic'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]

    rank = models.PositiveIntegerField(unique=True)
    domain = models.CharField(max_length=10, choices=DOMAIN)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=15, choices=LEVEL, default='Basic')
    explanation = models.TextField()
    example = models.TextField(blank=True, default='', help_text="Concrete example or interview-style follow-up illustrating the concept")
    reference_url = models.URLField(max_length=400, blank=True, default='',
                                     help_text="Direct link to the real GeeksforGeeks article for this concept")
    flowchart_mermaid = models.TextField(blank=True, default='',
                                          help_text="Mermaid.js flowchart definition rendered on the concept page")

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} {self.title}"


class TechQuestion(models.Model):
    DOMAIN = [
        ('OOP', 'Object Oriented Programming'), ('DBMS', 'DBMS'), ('OS', 'Operating Systems'),
        ('CN', 'Computer Networks'), ('SE', 'Software Engineering'), ('SD', 'System Design'),
    ]
    SOURCE = [('LeetCode', 'LeetCode'), ('GeeksforGeeks', 'GeeksforGeeks')]

    domain = models.CharField(max_length=10, choices=DOMAIN)
    question = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Medium')
    source = models.CharField(max_length=20, choices=SOURCE, default='GeeksforGeeks')
    link = models.URLField(max_length=400)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['domain', 'order']

    def __str__(self):
        return f"{self.question[:50]} [{self.domain}]"


class UserTechProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tech_progress')
    question = models.ForeignKey(TechQuestion, on_delete=models.CASCADE, related_name='progress')
    solved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')
