# Базовый образ
FROM python:3.8-slim

# Рабочая директория
WORKDIR /usr/src

# Убираем лишние записи на диск
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка зависимостей для python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Копируем проект
COPY . .