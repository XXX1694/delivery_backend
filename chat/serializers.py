from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatSession, ChatMessage
from users.serializers import UserSerializer  # Для отображения информации об отправителе


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для сообщений в чате.
    """
    # sender = UserSerializer(read_only=True) # Для полной информации об отправителе
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_phone_number = serializers.CharField(source='sender.phone_number', read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'chat_session', 'sender_id', 'sender_phone_number',
            'text_content', 'timestamp', 'is_read'
        ]
        read_only_fields = ['chat_session', 'sender_id', 'sender_phone_number', 'timestamp']
        # Клиент отправляет только 'text_content'

    def create(self, validated_data):
        # Логика создания сообщения будет в perform_create во View
        return super().create(validated_data)


class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для сессии чата. Может включать последние сообщения.
    """

    # messages = ChatMessageSerializer(many=True, read_only=True) # Можно включить, если нужно получать сообщения вместе с сессией

    class Meta:
        model = ChatSession
        fields = ['id', 'order', 'created_at', 'updated_at']