FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p uploads/media && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]
