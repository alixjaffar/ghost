FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Database lives on a mounted persistent volume in production
ENV DATABASE_PATH=/data/ghost.db
RUN mkdir -p /data

EXPOSE 8000

# Render/most platforms inject $PORT; default to 8000 locally
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
