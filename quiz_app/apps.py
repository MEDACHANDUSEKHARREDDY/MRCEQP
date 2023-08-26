from django.apps import AppConfig


class QuizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz_app'

default_app_config = 'your_app.apps.YourAppConfig'
