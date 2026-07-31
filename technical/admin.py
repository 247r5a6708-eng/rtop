from django.contrib import admin
from .models import Concept, TechQuestion, UserTechProgress
admin.site.register(Concept)
admin.site.register(TechQuestion)
admin.site.register(UserTechProgress)
