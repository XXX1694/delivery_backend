from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings # Чтобы ссылаться на AUTH_USER_MODEL
from users.models import ClientProfile, CourierProfile # Прямой импорт профилей
from core.models import City, PackageSize

class OrderStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название статуса')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    # Порядок для отображения или логики смены статусов, если потребуется
    order_index = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'
        ordering = ['order_index', 'name']

def generate_unique_order_id():
    """Генерирует уникальный ID для заказа (12 символов, буквы и цифры)"""
    # Проверяем уникальность, хотя вероятность коллизии при 12 символах крайне мала
    # для get_random_string(12, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
    # (убрали I, O, 0, 1 для читаемости, если нужно)
    while True:
        order_id = get_random_string(12, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        if not Order.objects.filter(unique_order_id=order_id).exists():
            return order_id

class Order(models.Model):
    # Связи
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.PROTECT, # Защита от удаления клиента, если у него есть заказы
        related_name='orders_as_client',
        verbose_name='Клиент (Отправитель)'
    )
    courier = models.ForeignKey(
        CourierProfile,
        on_delete=models.SET_NULL,
        null=True, blank=True, # Курьер может быть не назначен сразу
        related_name='orders_as_courier',
        verbose_name='Курьер'
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.PROTECT, # Статус не должен удаляться, если он используется
        verbose_name='Статус заказа'
    )
    package_size = models.ForeignKey(
        PackageSize,
        on_delete=models.SET_NULL, null=True, # Размер может стать неактуальным, но заказ остается
        verbose_name='Размер заказа'
    )

    # Информация об отправке и доставке
    origin_city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='origin_orders',
        verbose_name='Город отправки'
    )
    destination_city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='destination_orders',
        verbose_name='Город доставки'
    )
    pickup_address = models.CharField(max_length=255, verbose_name='Адрес забора')
    delivery_address = models.CharField(max_length=255, verbose_name='Адрес доставки')

    # Время
    pickup_date = models.DateField(verbose_name='Желаемая дата забора')
    pickup_time_slot = models.CharField(max_length=100, verbose_name='Желаемый временной промежуток забора') # Например, "10:00-12:00"

    # Получатель
    recipient_name = models.CharField(max_length=255, verbose_name='Имя получателя')
    recipient_phone = models.CharField(max_length=20, verbose_name='Номер телефона получателя')

    # Отправитель (дублируем для истории, т.к. данные клиента могут измениться)
    # Изначально можно заполнять из client.full_name и client.user.phone_number
    sender_name_snapshot = models.CharField(max_length=255, verbose_name='ФИО отправителя (на момент заказа)')
    sender_phone_snapshot = models.CharField(max_length=20, verbose_name='Телефон отправителя (на момент заказа)')

    # Дополнительно
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')
    unique_order_id = models.CharField(
        max_length=12, unique=True, default=generate_unique_order_id, editable=False, verbose_name='Уникальный ID заказа'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена доставки')

    # Временные метки выполнения
    pickup_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Время фактического забора заказа')
    delivery_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Время фактической доставки заказа')
    cancellation_reason = models.TextField(blank=True, null=True, verbose_name='Причина отмены')


    # Временные метки создания/обновления
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self):
        return f"Заказ {self.unique_order_id} от {self.client.full_name}"

    def save(self, *args, **kwargs):
        if not self.pk: # Если это новый объект (еще не сохранен в БД)
            # Заполняем данные отправителя из профиля клиента
            self.sender_name_snapshot = self.client.full_name
            self.sender_phone_snapshot = self.client.user.phone_number
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']