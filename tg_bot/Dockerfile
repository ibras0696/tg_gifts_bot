FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app:/database

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код проекта (весь)
COPY . .

# Запуск бота
CMD ["python", "main.py"]
