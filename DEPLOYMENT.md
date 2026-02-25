# RADHEY AI LIFE OS - Deployment Guide

## 1. System Requirements

### Recommended Hardware:
- 4 GB RAM or higher
- 2 CPU cores or more
- At least 10 GB of free disk space
- SSD storage recommended for faster OCR processing

### Supported Platforms:
- Ubuntu 18.04+ (Recommended)
- CentOS 7+
- Debian 10+
- macOS 10.14+
- Windows 10+ (with WSL2 for better performance)

## 2. Installation Steps

### Step 1: Install System Dependencies

#### Ubuntu/Debian:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    poppler-utils \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libopencv-dev \
    pkg-config
```

#### CentOS:
```bash
# Enable EPEL repository
sudo yum install -y epel-release

# Install required packages
sudo yum install -y \
    tesseract \
    tesseract-langpack-hin \
    poppler-utils \
    python3-pip \
    python3-venv \
    git \
    gcc \
    gcc-c++ \
    make \
    opencv-devel
```

#### macOS (Homebrew):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Tesseract with Hindi language pack
brew install tesseract
brew install tesseract-lang
```

#### Windows:
1. Download Tesseract installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. During installation, ensure "Hindi (hin)" language pack is selected
3. Add Tesseract to system PATH
4. Verify installation with: `tesseract --version`

### Step 2: Verify Tesseract Installation

```bash
# Check Tesseract version
tesseract --version

# Check if Hindi language pack is installed
tesseract --list-langs | grep hin
```

You should see: `hin` in the list of available languages.

### Step 3: Install Python Dependencies

```bash
# Clone repository
git clone <repository-url>
cd radhey_ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

Required variables:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `MONGODB_URI`: MongoDB connection string (local or Atlas)
- `MONGODB_DB`: Database name (default: radhey_ai_db)
- `TESSERACT_PATH`: Path to tesseract executable (auto-detected, but may need to specify on Windows)

### Step 5: Start MongoDB

#### Local MongoDB (Ubuntu):
```bash
# Install MongoDB
sudo apt install -y mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Verify MongoDB connection
mongo --eval "db.adminCommand('ping')"
```

#### MongoDB Atlas (Cloud):
1. Create an account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Add your server's IP to the whitelist
4. Create a database user
5. Copy the connection string

### Step 6: Run the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python bot/main.py
```

## 3. Production Deployment

### Option 1: Systemd Service (Ubuntu/Debian)

Create a systemd service file:
```bash
sudo nano /etc/systemd/system/radhey-ai-bot.service
```

Add the following content:
```ini
[Unit]
Description=Radhey AI Telegram Bot
After=network.target mongodb.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/radhey_ai
ExecStart=/path/to/venv/bin/python /path/to/radhey_ai/bot/main.py
Restart=always
RestartSec=10
Environment=PATH=/path/to/venv/bin
Environment=PYTHONPATH=/path/to/radhey_ai

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the bot service
sudo systemctl start radhey-ai-bot

# Enable at startup
sudo systemctl enable radhey-ai-bot

# Check status
sudo systemctl status radhey-ai-bot

# View logs
journalctl -u radhey-ai-bot -f
```

### Option 2: Docker Deployment

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    poppler-utils \
    libopencv-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .env file (or mount as volume)
COPY .env.example .env

# Set environment variables
ENV PYTHONPATH=/app
ENV TESSERACT_PATH=/usr/bin/tesseract

# Run the bot
CMD ["python", "bot/main.py"]
```

Build and run:
```bash
# Build Docker image
docker build -t radhey-ai-bot .

# Run Docker container
docker run -d \
  --name radhey-ai-bot \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env \
  radhey-ai-bot
```

### Option 3: Deployment on Render.com

1. Create a Render account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python bot/main.py`
   - Environment variables from .env file

## 4. Performance Optimization

### 1. OCR Optimization

```python
# Modify core/ocr_engine.py for better performance
# Reduce DPI for faster processing (from 300 to 200)
def convert_scanned_pdf_to_images(self, pdf_path, dpi=200):
    ...
```

### 2. Caching

```python
# Add Redis caching for OCR results
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Cache OCR results
def cache_ocr_result(key, result):
    r.setex(key, 3600, json.dumps(result))

# Get cached result
def get_cached_result(key):
    result = r.get(key)
    return json.loads(result) if result else None
```

### 3. Async Processing

```python
# Using Celery for async task processing
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_file_async(file_path, user_id):
    # OCR processing logic here
    ...
```

## 5. Monitoring and Logging

### Enable Logging

```python
# In bot/main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure file logging
file_handler = RotatingFileHandler(
    'radhey-ai.log',
    maxBytes=1024*1024*10,  # 10 MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Add handler to logger
logger.addHandler(file_handler)
```

### Health Check

```python
# Create a simple health check endpoint
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 6. Troubleshooting

### Common Issues

1. **Tesseract not found**:
   ```bash
   # Check Tesseract installation
   which tesseract
   # Add to PATH or update TESSERACT_PATH in .env
   ```

2. **Hindi language pack missing**:
   ```bash
   sudo apt install tesseract-ocr-hin  # Ubuntu
   tesseract --list-langs  # Verify
   ```

3. **Memory issues**:
   - Reduce DPI in PDF to image conversion
   - Increase server memory or enable swap

4. **Slow processing**:
   - Upgrade to SSD storage
   - Use faster CPU
   - Optimize image preprocessing

## 7. Security Best Practices

1. **Environment Variables**: Never commit .env file to version control
2. **HTTPS**: Use webhooks with HTTPS
3. **Rate Limiting**: Implement request throttling
4. **Data Sanitization**: Validate all inputs
5. **Database Security**: Use strong passwords and restricted IP access
6. **Dependency Updates**: Regularly update Python packages

## 8. Backup and Restore

### Backing up MongoDB

```bash
# Create backup
mongodump --uri="mongodb://localhost:27017/radhey_ai_db" --out=./backup/

# Restore from backup
mongorestore --uri="mongodb://localhost:27017/radhey_ai_db" ./backup/
```

### Auto Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mongodump --uri="mongodb://localhost:27017/radhey_ai_db" --out="$BACKUP_DIR/$TIMESTAMP"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} \;
```

## 9. Updating the Bot

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart radhey-ai-bot
```

## 10. Support

For issues or support:
1. Check logs at `/var/log/syslog` (Ubuntu) or `journalctl -u radhey-ai-bot`
2. Visit our GitHub repository for issues
3. Join our Telegram support group: @radheyaiteam
