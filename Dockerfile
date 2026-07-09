FROM python:3.10-slim

WORKDIR /app

# 🔥 system deps (BUILD + AUDIO)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libsndfile1 \
    libopus-dev \
    libopus0 \
    libsoxr-dev \
    && rm -rf /var/lib/apt/lists/*

# 🔥 env (important pour logs + perf)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 🔥 install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 🔥 app
COPY . .

# ⚠️ IMPORTANT: match ton uvicorn port
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]