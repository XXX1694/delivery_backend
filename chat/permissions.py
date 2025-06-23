from rest_framework import permissions
from .models import ChatSession


class IsChatParticipant(permissions.BasePermission):
    """
    Разрешение, которое проверяет, является ли пользователь участником чата.
    Участники - это клиент заказа и назначенный курьер.
    """

    def has_object_permission(self, request, view, obj):
        # obj здесь - это экземпляр ChatSession
        if request.user and request.user.is_authenticated:
            if isinstance(obj, ChatSession):
                chat_session = obj
            elif hasattr(obj, 'chat_session'):  # Для ChatMessage
                chat_session = obj.chat_session
            else:
                return False

            if request.user.is_staff:
                return True  # Администраторы имеют доступ ко всему

            # Проверяем, является ли пользователь клиентом или курьером этого заказа
            return (chat_session.order.client.user == request.user or
                    (chat_session.order.courier and chat_session.order.courier.user == request.user))

        return False