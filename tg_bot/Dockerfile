FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app:/database

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота
COPY ./tg_bot .

# Команда запуска
CMD ["python", "main.py"]
