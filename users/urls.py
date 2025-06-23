from django.urls import path
from .views import (
    ClientRegistrationAPIView,
    CustomAuthTokenLoginView,
    UserDetailAPIView,
    CourierRegistrationAPIView # <--- Импортируем новое представление
)

app_name = 'users_api' # Хорошая практика - задавать app_name

urlpatterns = [
    path('register/client/', ClientRegistrationAPIView.as_view(), name='client_register'),
    path('register/courier/', CourierRegistrationAPIView.as_view(), name='courier_register'), # <--- НОВЫЙ ПУТЬ
    path('login/', CustomAuthTokenLoginView.as_view(), name='api_token_auth'),
    path('me/', UserDetailAPIView.as_view(), name='user_detail'),
]