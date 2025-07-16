FROM python:3.12-slim

# Установка системных зависимостей для playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libgbm1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app:/database

# Копируем зависимости
COPY requirements.txt .

# Установка зависимостей и playwright
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps

# Копируем исходный код
COPY ./gifts_system .

# Команда запуска
CMD ["python", "main.py"]
