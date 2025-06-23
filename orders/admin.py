# orders/admin.py
from django.contrib import admin
from .models import OrderStatus, Order


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order_index')
    ordering = ('order_index',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'unique_order_id', 'client', 'courier', 'status', 'origin_city',
        'destination_city', 'price', 'pickup_date', 'created_at'
    )
    list_filter = ('status', 'origin_city', 'destination_city', 'pickup_date', 'created_at')
    search_fields = (
        'unique_order_id', 'client__full_name', 'client__user__phone_number',
        'courier__full_name', 'courier__user__phone_number', 'recipient_name', 'recipient_phone'
    )
    readonly_fields = ('unique_order_id', 'sender_name_snapshot', 'sender_phone_snapshot', 'created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('unique_order_id', 'client', 'courier', 'status', 'price')
        }),
        ('Отправитель и Получатель', {
            'fields': ('sender_name_snapshot', 'sender_phone_snapshot', 'recipient_name', 'recipient_phone')
        }),
        ('Маршрут и детали', {
            'fields': ('origin_city', 'pickup_address', 'destination_city', 'delivery_address', 'package_size',
                       'comment')
        }),
        ('Время', {
            'fields': ('pickup_date', 'pickup_time_slot', 'pickup_timestamp', 'delivery_timestamp')
        }),
        ('Причина отмены (если применимо)', {
            'fields': ('cancellation_reason',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Скрываемое поле
        }),
    )

    # Для удобства выбора client и courier, можно использовать raw_id_fields, если их много
    # raw_id_fields = ('client', 'courier', 'status', 'package_size', 'origin_city', 'destination_city')