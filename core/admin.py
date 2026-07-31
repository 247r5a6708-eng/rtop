from django.contrib import admin
from .models import ActivityLog, Profile, Badge

admin.site.register(ActivityLog)
admin.site.register(Profile)
admin.site.register(Badge)
