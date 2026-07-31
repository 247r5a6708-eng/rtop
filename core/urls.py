from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/restore-streak/', views.restore_streak, name='restore_streak'),
]
