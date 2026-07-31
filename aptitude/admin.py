from django.contrib import admin
from .models import Topic, Problem, UserProblemProgress
admin.site.register(Topic)
admin.site.register(Problem)
admin.site.register(UserProblemProgress)
