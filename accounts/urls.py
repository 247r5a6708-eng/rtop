from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.PirateResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PirateResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PirateResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PirateResetCompleteView.as_view(), name='password_reset_complete'),
]
