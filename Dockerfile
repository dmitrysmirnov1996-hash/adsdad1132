FROM python:3.10-slim

# Устанавливаем системные зависимости, включая gcc и python3-dev
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Хак для Python 3.11: создаём симлинк на longintrepr.h
# Это решает проблему "longintrepr.h: No such file or directory"
RUN ln -s /usr/local/include/python3.11/cpython/longintrepr.h /usr/local/include/python3.11/longintrepr.h || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ставим Maigret как Python-пакет
RUN pip install --no-cache-dir maigret

COPY app.py .

CMD ["python", "app.py"]
