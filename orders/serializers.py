from rest_framework import serializers
from .models import Order, OrderStatus # Модели из текущего приложения orders

# Импорты сериализаторов из других приложений для использования в to_representation
from users.serializers import ClientProfileSerializer, CourierProfileSerializer
from core.serializers import CitySerializer as CoreCitySerializer # Используем алиас для ясности
from core.serializers import PackageSizeSerializer as CorePackageSizeSerializer # Используем алиас для ясности

# --- ДОБАВЬТЕ ЭТИ ИМПОРТЫ МОДЕЛЕЙ ---
from core.models import City, PackageSize # Модели из приложения core
# ------------------------------------

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description', 'order_index']


class OrderSerializer(serializers.ModelSerializer):
    # Для чтения (используем сериализаторы, импортированные с алиасами или напрямую)
    client = ClientProfileSerializer(read_only=True)
    courier = CourierProfileSerializer(read_only=True, required=False)
    status = OrderStatusSerializer(read_only=True)  # Используем локальный OrderStatusSerializer
    package_size = CorePackageSizeSerializer(read_only=True)  # Используем импортированный CorePackageSizeSerializer
    origin_city = CoreCitySerializer(read_only=True)  # Используем импортированный CoreCitySerializer
    destination_city = CoreCitySerializer(read_only=True)  # Используем импортированный CoreCitySerializer

    # Поля только для записи (используем импортированные МОДЕЛИ для queryset)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderStatus.objects.all(), source='status', write_only=True, required=False
    )
    package_size_id = serializers.PrimaryKeyRelatedField(
        queryset=PackageSize.objects.all(), source='package_size', write_only=True  # Теперь PackageSize известен
    )
    origin_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='origin_city', write_only=True  # Теперь City известен
    )
    destination_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='destination_city', write_only=True  # Теперь City известен
    )

    class Meta:
        model = Order
        fields = [
            'id', 'unique_order_id',
            'client', 'courier', 'status',
            'package_size', 'origin_city', 'destination_city',
            'pickup_address', 'delivery_address',
            'pickup_date', 'pickup_time_slot',
            'recipient_name', 'recipient_phone',
            'sender_name_snapshot', 'sender_phone_snapshot',
            'comment', 'price',
            'pickup_timestamp', 'delivery_timestamp', 'cancellation_reason',
            'created_at', 'updated_at',

            'package_size_id', 'origin_city_id', 'destination_city_id', 'status_id'
        ]
        read_only_fields = [
            'id', 'unique_order_id', 'client', 'courier', 'status',
            'sender_name_snapshot', 'sender_phone_snapshot',
            'pickup_timestamp', 'delivery_timestamp', 'cancellation_reason',
            'created_at', 'updated_at',
            # Поля package_size, origin_city, destination_city тоже неявно read_only
            # из-за того, как мы их определили выше для чтения, а для записи используем *_id поля.
            # Можно добавить их сюда для явности, если хотите.
        ]

    # Метод to_representation я немного изменил, чтобы он использовал импортированные сериализаторы,
    # а для статуса - локальный OrderStatusSerializer.
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = ClientProfileSerializer(instance.client).data if instance.client else None
        representation['courier'] = CourierProfileSerializer(instance.courier).data if instance.courier else None
        representation['status'] = OrderStatusSerializer(instance.status).data if instance.status else None
        representation['package_size'] = CorePackageSizeSerializer(
            instance.package_size).data if instance.package_size else None
        representation['origin_city'] = CoreCitySerializer(instance.origin_city).data if instance.origin_city else None
        representation['destination_city'] = CoreCitySerializer(
            instance.destination_city).data if instance.destination_city else None
        return representation
