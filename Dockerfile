FROM python:3.11-slim-buster

# Используем современный синтаксис ENV key=value
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем netcat для проверки доступности БД и очищаем кэш apt
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

# Копируем entrypoint.sh в контейнер
COPY ./entrypoint.sh /app/entrypoint.sh

# Даем права на выполнение нашему скрипту
RUN chmod +x /app/entrypoint.sh

# Копируем остальной код проекта
COPY . .

# Указываем, что при старте контейнера нужно выполнить наш скрипт
ENTRYPOINT ["/app/entrypoint.sh"]