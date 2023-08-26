from django.urls import path
from . import views

urlpatterns = [
    path('user_details/', views.user_details, name='user_details'),
    path('send-verification-email/', views.send_verification_email, name='send_verification_email'), 
    path('verify-email/', views.verify_email, name='verify_email'),
    path('quiz/', views.quiz, name='quiz'),
    path('user_details/quiz/<int:question_number>/', views.quiz, name='quiz_with_number'),
    path('quiz_finished/', views.quiz_finished, name='quiz_finished'),
    
    # Add the URL pattern for fetching user responses
    path('get_user_responses/', views.get_user_responses, name='get_user_responses'),
]
