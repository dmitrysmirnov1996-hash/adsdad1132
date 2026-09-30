FROM python:3.11-slim

# Устанавливаем Docker CLI (чтобы можно было запускать контейнеры Maigret)
RUN apt-get update && apt-get install -y docker.io

WORKDIR /app
COPY app.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
