FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ставим Maigret как Python-пакет
RUN pip install --no-cache-dir maigret

COPY app.py .

CMD ["python", "app.py"]
