# orders/urls.py
from django.urls import path
from .views import (
    OrderStatusListAPIView,
    OrderListCreateAPIView,
    OrderDetailAPIView,
    AvailableOrderListAPIView # <--- Импортируем новое представление
)

app_name = 'orders_api'

urlpatterns = [
    path('statuses/', OrderStatusListAPIView.as_view(), name='orderstatus_list'),
    path('', OrderListCreateAPIView.as_view(), name='order_list_create'),
    path('available/', AvailableOrderListAPIView.as_view(), name='available_order_list'), # <--- НОВЫЙ ПУТЬ
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order_detail_update'),
]