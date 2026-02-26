# Lightweight Python base
FROM python:3.11-slim

# Ensure noninteractive apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set timezone via ENV (override at runtime with -e TZ=Asia/Kolkata)
ENV TZ=Etc/UTC

# System deps for common Python libs and OCR
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
       ca-certificates \
       tzdata \
       tesseract-ocr \
       tesseract-ocr-hin \
       poppler-utils \
       libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Copy dependency files first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Permissions
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck: ensure python is functional and process is alive
HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
  CMD python -c "import sys; print(sys.version_info)"

# Default command: start telegram bot
# TELEGRAM_BOT_TOKEN must be provided via environment
ENV PYTHONPATH=/app
CMD ["python", "-m", "bot.main"]
