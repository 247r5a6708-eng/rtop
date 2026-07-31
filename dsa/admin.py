from django.contrib import admin
from .models import Pattern, Question, UserQuestionProgress
admin.site.register(Pattern)
admin.site.register(Question)
admin.site.register(UserQuestionProgress)
