from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    ClientRegistrationSerializer,
    UserSerializer,
    CourierRegistrationSerializer # <--- Импортируем новый сериализатор
)

User = get_user_model()

class ClientRegistrationAPIView(generics.CreateAPIView):
    serializer_class = ClientRegistrationSerializer  # Используется для валидации и создания
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # serializer.save() вызовет serializer.create()

        # Формируем ответ с помощью UserSerializer
        # чтобы структура ответа была консистентной с тем, как мы получаем данные пользователя
        response_data_serializer = UserSerializer(user, context=self.get_serializer_context())

        headers = self.get_success_headers(response_data_serializer.data)
        return Response(response_data_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    # Можно переопределить perform_create, если нужно что-то сделать после создания,
    # например, сразу выдать токен. Но обычно токен получают через отдельный login эндпоинт.

class CustomAuthTokenLoginView(ObtainAuthToken):
    """
    Представление для входа пользователя и получения токена.
    Возвращает токен, id пользователя, номер телефона и роль.
    """
    permission_classes = [permissions.AllowAny] # Разрешить всем делать запросы на логин

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request}) # Получаем данные пользователя
        return Response({
            'token': token.key,
            'user': user_serializer.data # Включаем информацию о пользователе
        })

class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Только аутентифицированные пользователи

    def get_object(self):
        # Возвращает текущего аутентифицированного пользователя
        return self.request.user


class CourierRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CourierRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    # --- Указываем парсеры для обработки multipart/form-data (файлы) ---
    parser_classes = [MultiPartParser, FormParser]

    # -----------------------------------------------------------------

    # Так же, как и в ClientRegistrationAPIView, переопределим create для консистентного ответа
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # serializer.save() вызовет serializer.create()

        # Формируем ответ с помощью UserSerializer
        response_data_serializer = UserSerializer(user, context=self.get_serializer_context())

        headers = self.get_success_headers(response_data_serializer.data)
        return Response(response_data_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
