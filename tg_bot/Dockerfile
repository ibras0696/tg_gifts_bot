FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app:/database

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект, чтобы был и /app и /database
COPY ./tg_bot /app
COPY ./database /database

CMD ["python", "main.py"]
