from .base import *

DEBUG = False # Никогда не включайте DEBUG=True на production!

# Замените 'your_domain.com' на реальный домен вашего сайта
# Также можно добавить IP-адрес вашего сервера
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['your_domain.com', '127.0.0.1'])

# Используем переменные окружения для подключения к PostgreSQL
DATABASES = {
    'default': env.db(),
}