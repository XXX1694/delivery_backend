
from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):  # Или StackedInline
    model = ChatMessage
    extra = 0  # Не показывать пустые формы для добавления по умолчанию
    readonly_fields = ('sender', 'text_content', 'timestamp', 'is_read')
    can_delete = False
    ordering = ('timestamp',)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('order__unique_order_id', 'order__client__full_name', 'order__courier__full_name')
    readonly_fields = ('order', 'created_at', 'updated_at')
    inlines = [ChatMessageInline]

    def order_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.order:
            link = reverse("admin:orders_order_change",
                           args=[obj.order.id])  # Убедитесь, что это правильный admin URL name
            return format_html('<a href="{}">{}</a>', link, obj.order.unique_order_id)
        return "Нет заказа"

    order_link.short_description = 'Заказ ID'
    order_link.admin_order_field = 'order'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_session_info', 'sender_info', 'short_text', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'chat_session')
    search_fields = ('text_content', 'sender__phone_number', 'chat_session__order__unique_order_id')
    readonly_fields = ('chat_session', 'sender', 'text_content', 'timestamp')
    list_editable = ('is_read',)

    def chat_session_info(self, obj):
        return str(obj.chat_session)

    chat_session_info.short_description = 'Чат сессия'

    def sender_info(self, obj):
        return obj.sender.phone_number if obj.sender else "N/A"

    sender_info.short_description = 'Отправитель'

    def short_text(self, obj):
        return (obj.text_content[:75] + '...') if len(obj.text_content) > 75 else obj.text_content

    short_text.short_description = 'Текст'