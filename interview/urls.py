from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('question/<int:qid>/toggle/', views.toggle_question, name='toggle_question'),
]
