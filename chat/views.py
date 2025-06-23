from rest_framework import generics, permissions
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .permissions import IsChatParticipant  # Импортируем наше разрешение
from users.models import User


class ChatSessionListAPIView(generics.ListAPIView):
    """
    Возвращает список чат-сессий для текущего пользователя (клиента или курьера).
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CLIENT and hasattr(user, 'client_profile'):
            return ChatSession.objects.filter(order__client=user.client_profile)
        elif user.role == User.ROLE_COURIER and hasattr(user, 'courier_profile'):
            return ChatSession.objects.filter(order__courier=user.courier_profile)
        return ChatSession.objects.none()


class ChatMessageListCreateAPIView(generics.ListCreateAPIView):
    """
    Возвращает список сообщений в чате или создает новое сообщение.
    Доступно только участникам чата.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        """
        Возвращает сообщения только для указанной в URL сессии чата.
        """
        session_id = self.kwargs.get('session_id')
        try:
            chat_session = ChatSession.objects.get(id=session_id)
            # Проверяем права доступа к объекту chat_session
            self.check_object_permissions(self.request, chat_session)
            return chat_session.messages.all()
        except ChatSession.DoesNotExist:
            return ChatMessage.objects.none()

    def perform_create(self, serializer):
        """
        При создании нового сообщения, устанавливаем отправителя и сессию чата.
        """
        session_id = self.kwargs.get('session_id')
        try:
            chat_session = ChatSession.objects.get(id=session_id)
            # Проверяем права доступа к объекту chat_session
            self.check_object_permissions(self.request, chat_session)

            # Обновляем `updated_at` у чат сессии при новом сообщении
            chat_session.save()  # Просто вызываем save, чтобы `auto_now=True` сработало

            serializer.save(sender=self.request.user, chat_session=chat_session)
        except ChatSession.DoesNotExist:
            raise serializers.ValidationError("Чат сессия с указанным ID не найдена.")