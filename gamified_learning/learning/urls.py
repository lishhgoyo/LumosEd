from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('complete_task/', views.complete_task, name='complete_task'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('rewards/', views.rewards, name='rewards'),
    path('daily-challenge/', views.daily_challenge, name='daily_challenge'),
    path('recommendations/', views.personalized_recommendations, name='personalized_recommendations'),
    path('quiz/', views.personalized_quiz, name='personalized_quiz'),
    
]
