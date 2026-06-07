FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg wget unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Завантажуємо моделі Vosk під час збірки образу (~1.6 ГБ)
RUN python download_models.py

# Hugging Face Spaces вимагає відкритий порт 7860
EXPOSE 7860

CMD ["python", "bot.py"]
