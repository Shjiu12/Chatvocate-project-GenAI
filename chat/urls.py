
from django.urls import path
from .views import chat_question

urlpatterns = [
    path("chat/", chat_question, name="chat-question"),
]