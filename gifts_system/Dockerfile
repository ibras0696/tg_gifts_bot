FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl wget gnupg ca-certificates \
    fonts-liberation libnss3 libatk-bridge2.0-0 \
    libxss1 libasound2 libgbm1 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH=/app:/app/database

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && playwright install --with-deps

COPY ./gifts_system /app
COPY ./database /app/database

CMD ["python", "main.py"]
