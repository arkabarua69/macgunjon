from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_home, name='chatbot_home'),
    path('message/', views.chatbot_message, name='chatbot_message'),
]
