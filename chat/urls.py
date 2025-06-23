from django.urls import path
from .views import ChatSessionListAPIView, ChatMessageListCreateAPIView

app_name = 'chat_api'

urlpatterns = [
    # Список чатов для пользователя
    path('', ChatSessionListAPIView.as_view(), name='chat_session_list'),

    # Список сообщений и создание нового сообщения для конкретного чата
    path('<int:session_id>/messages/', ChatMessageListCreateAPIView.as_view(), name='chat_message_list_create'),
]