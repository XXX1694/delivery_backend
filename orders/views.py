# orders/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Order, OrderStatus
from .serializers import OrderSerializer, OrderStatusSerializer
from users.models import User
from chat.models import ChatSession  # <--- ДОБАВЬТЕ ЭТОТ ИМПОРТ


class OrderStatusListAPIView(generics.ListAPIView):
    queryset = OrderStatus.objects.all().order_by('order_index')
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.AllowAny]


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CLIENT and hasattr(user, 'client_profile'):
            return Order.objects.filter(client=user.client_profile).order_by('-created_at')
        elif user.role == User.ROLE_COURIER and hasattr(user, 'courier_profile'):
            return Order.objects.filter(courier=user.courier_profile).order_by('-created_at')
        elif user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.none()

    def perform_create(self, serializer):
        if not (self.request.user.role == User.ROLE_CLIENT and hasattr(self.request.user, 'client_profile')):
            raise serializers.ValidationError(
                {"detail": "Только клиенты могут создавать заказы."},
                code=status.HTTP_403_FORBIDDEN
            )

        client_profile = self.request.user.client_profile

        try:
            initial_status_name = "Обработка"
            initial_status = OrderStatus.objects.get(name=initial_status_name)
        except OrderStatus.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": f"Начальный статус заказа '{initial_status_name}' не настроен в системе."},
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer.save(client=client_profile, status=initial_status)


class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if user.is_staff:
            return obj

        is_client_owner = (user.role == User.ROLE_CLIENT and
                           hasattr(user, 'client_profile') and
                           obj.client == user.client_profile)

        is_assigned_courier = (user.role == User.ROLE_COURIER and
                               hasattr(user, 'courier_profile') and
                               obj.courier == user.courier_profile)

        is_available_for_courier_to_take = (user.role == User.ROLE_COURIER and
                                            obj.courier is None and
                                            obj.status.name == "Обработка")

        if is_client_owner or is_assigned_courier or is_available_for_courier_to_take:
            return obj

        raise permissions.PermissionDenied("У вас нет прав для доступа к этому заказу.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        user = request.user

        if (user.role == User.ROLE_COURIER and
                hasattr(user, 'courier_profile') and
                instance.courier is None and
                instance.status.name == "Обработка"):

            try:
                new_status_name = "В пути"
                new_status = OrderStatus.objects.get(name=new_status_name)
            except OrderStatus.DoesNotExist:
                return Response(
                    {"error": f"Статус '{new_status_name}' для взятия заказа не найден."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            instance.courier = user.courier_profile
            instance.status = new_status
            instance.pickup_timestamp = timezone.now()
            instance.save()

            # --- СОЗДАНИЕ ЧАТА ПРИ ВЗЯТИИ ЗАКАЗА ---
            ChatSession.objects.get_or_create(order=instance)
            # get_or_create вернет кортеж (object, created_boolean)
            # Это гарантирует, что чат будет создан только один раз для заказа.
            # ------------------------------------

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        elif (user.role == User.ROLE_COURIER and
              hasattr(user, 'courier_profile') and
              instance.courier == user.courier_profile):

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        elif (user.role == User.ROLE_CLIENT and
              hasattr(user, 'client_profile') and
              instance.client == user.client_profile):

            requested_status_id = request.data.get("status_id")
            if instance.status.name == "Обработка" and requested_status_id:
                try:
                    cancel_status = OrderStatus.objects.get(id=requested_status_id)
                    if "Отменен" in cancel_status.name:
                        data_for_update = {'status': cancel_status.id}
                        if "cancellation_reason" in request.data:
                            data_for_update['cancellation_reason'] = request.data.get("cancellation_reason")

                        serializer = self.get_serializer(instance, data=data_for_update, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)
                        return Response(serializer.data)
                    else:
                        return Response(
                            {"error": "Некорректный статус для отмены заказа."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except OrderStatus.DoesNotExist:
                    return Response(
                        {"error": "Указанный статус для отмены не найден."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"detail": "Обновление заказа клиентом не разрешено для данного статуса или данных."},
                status=status.HTTP_403_FORBIDDEN
            )

        raise permissions.PermissionDenied("Действие не разрешено для вашей роли или статуса заказа.")

    def perform_update(self, serializer):
        instance = serializer.instance
        validated_data = serializer.validated_data
        new_status = validated_data.get('status')

        if self.request.user.role == User.ROLE_COURIER:
            if new_status and new_status.name == "Доставлен" and not instance.delivery_timestamp:
                serializer.save(delivery_timestamp=timezone.now())
                return
        if self.request.user.role == User.ROLE_CLIENT and new_status and "Отменен" in new_status.name:
            if 'cancellation_reason' in validated_data:
                serializer.save(cancellation_reason=validated_data.get('cancellation_reason', "Отменено клиентом"))
                return

        serializer.save()


class AvailableOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_COURIER and hasattr(user, 'courier_profile'):
            try:
                available_status = OrderStatus.objects.get(name="Обработка")
                return Order.objects.filter(courier__isnull=True, status=available_status).order_by('-created_at')
            except OrderStatus.DoesNotExist:
                return Order.objects.none()
        return Order.objects.none()