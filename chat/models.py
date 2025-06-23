from django.db import models
from django.conf import settings  # Для ссылки на User модель
from orders.models import Order  # Для связи чата с заказом


class ChatSession(models.Model):
    """
    Представляет сессию чата, связанную с конкретным заказом,
    между клиентом заказа и назначенным курьером.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='chat_session',
        verbose_name='Заказ'
    )
    # Участники этого чата - клиент заказа и курьер заказа.
    # Мы можем не хранить их здесь явно, так как они есть в Order,
    # но для упрощения запросов и разрешений можно добавить.
    # Либо определять участников динамически через order.client.user и order.courier.user.
    # Пока оставим так, участники определяются через заказ.

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время последнего сообщения')

    def __str__(self):
        return f"Чат для заказа {self.order.unique_order_id}"

    class Meta:
        verbose_name = 'Чат сессия'
        verbose_name_plural = 'Чат сессии'
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """
    Представляет сообщение в чат сессии.
    """
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат сессия'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Ссылка на нашу кастомную модель User
        on_delete=models.SET_NULL,  # Если пользователь удален, сообщение остается, но отправитель неизвестен
        null=True,
        related_name='sent_chat_messages',
        verbose_name='Отправитель'
    )
    text_content = models.TextField(verbose_name='Текст сообщения')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')  # Базовая реализация статуса прочтения

    def __str__(self):
        sender_phone = self.sender.phone_number if self.sender else "Неизвестный отправитель"
        return f"Сообщение от {sender_phone} в {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = 'Сообщение в чате'
        verbose_name_plural = 'Сообщения в чатах'
        ordering = ['timestamp']  # Сообщения обычно отображаются в хронологическом порядке