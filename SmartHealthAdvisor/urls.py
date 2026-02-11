from django.urls import path
from . import views

urlpatterns = [
    # Home & Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Features
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chat-api/', views.chat_api, name='chat_api'), # Connects to ML Brain
    
    # Assessment
    path('assessment/', views.prakriti_assessment, name='prakriti_assessment'),
    path('save-prakriti/', views.save_prakriti_result, name='save_prakriti'), # Saves result to session

    # Recommendations (The error was here likely)
    path('yoga/', views.yoga_recommendation, name='yoga_recommendation'),
    
    # ⚠️ THIS IS THE LINE FIXING YOUR ERROR:
    path('diet/', views.personalized_diet_and_lifestyle, name='personalized_diet_and_lifestyle'),
    
    path('result/', views.result, name='result'),
    path('update-vitals/', views.update_vitals, name='update_vitals'),
    path('save-prakriti/', views.save_prakriti_result, name='save_prakriti')
]