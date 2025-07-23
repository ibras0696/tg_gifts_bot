FROM python:3.12-slim

WORKDIR /app

# Указываем PYTHONPATH для Python
ENV PYTHONPATH=/app:/app/database

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё из tg_bot в /app
COPY ./tg_bot /app

# Копируем database внутрь /app/database
COPY ./database /app/database

CMD ["python", "main.py"]
