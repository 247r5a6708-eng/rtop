from django.urls import path
from . import views

app_name = 'aptitude'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('problem/<int:pid>/toggle/', views.toggle_problem, name='toggle_problem'),
]
