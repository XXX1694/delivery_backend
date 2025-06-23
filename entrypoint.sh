#!/bin/sh

# Проверяем, доступны ли хост и порт базы данных
while ! nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 1
done

echo "PostgreSQL started"

# Выполняем миграции, собираем статику и запускаем Gunicorn
python manage.py migrate
python manage.py collectstatic --noinput --clear
gunicorn jibekjoly_backend.wsgi:application --bind 0.0.0.0:8000

exec "$@"