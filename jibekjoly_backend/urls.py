from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls', namespace='users_api')),
    path('api/v1/core/', include('core.urls', namespace='core_api')),
    path('api/v1/orders/', include('orders.urls', namespace='orders_api')),
    path('api/v1/chats/', include('chat.urls', namespace='chat_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)