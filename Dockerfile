FROM python:3.11-slim-buster

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1  # Запрещает Python создавать .pyc файлы
ENV PYTHONUNBUFFERED 1         # Вывод Python будет сразу отправляться в терминал (полезно для логов)

# Создаем рабочую директорию внутри контейнера
WORKDIR /app

# Обновляем pip
RUN python -m pip install --upgrade pip

# Копируем файл с зависимостями в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем весь код проекта в рабочую директорию /app
COPY . .