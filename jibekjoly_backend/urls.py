from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- ДОБАВЬТЕ ЭТИ ИМПОРТЫ ---
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# -----------------------------

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ваши API эндпоинты
    path('api/v1/users/', include('users.urls', namespace='users_api')),
    path('api/v1/core/', include('core.urls', namespace='core_api')),
    path('api/v1/orders/', include('orders.urls', namespace='orders_api')),
    path('api/v1/chats/', include('chat.urls', namespace='chat_api')),

    # --- ДОБАВЬТЕ ЭТИ ПУТИ ДЛЯ ДОКУМЕНТАЦИИ ---
    # Путь для скачивания файла схемы OpenAPI (schema.yml)
    path('api/v1/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Опционально:
    # Интерактивная документация Swagger UI
    path('api/v1/docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Альтернативная документация ReDoc
    path('api/v1/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # ---------------------------------------------
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)