from django.urls import path
from . import views

app_name = 'technical'

urlpatterns = [
    path('concepts/', views.concept_list, name='concept_list'),
    path('concepts/<int:rank>/', views.concept_detail, name='concept_detail'),
    path('questions/', views.question_list, name='question_list'),
    path('question/<int:qid>/toggle/', views.toggle_question, name='toggle_question'),
]
