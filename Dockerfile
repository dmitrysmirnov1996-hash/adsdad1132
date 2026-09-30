FROM python:3.11-slim

# Устанавливаем системные зависимости для сборки
# gcc — компилятор C
# python3-dev — заголовочные файлы Python
# libfreetype6-dev, libjpeg-dev, libffi-dev — для reportlab (PDF)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ставим Maigret как Python-пакет
RUN pip install --no-cache-dir maigret

COPY app.py .

CMD ["python", "app.py"]
