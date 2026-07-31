from django.urls import path
from . import views

app_name = 'dsa'

urlpatterns = [
    path('', views.pattern_list, name='pattern_list'),
    path('<slug:slug>/', views.pattern_detail, name='pattern_detail'),
    path('question/<int:qid>/toggle/', views.toggle_question, name='toggle_question'),
]
