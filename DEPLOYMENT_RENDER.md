# Render Deployment Guide (Radhey AI Life Commander)

This project is containerized for 24x7 deployment on Render using a Dockerfile and a blueprint (render.yaml).

## Prerequisites
- Render account (https://render.com)
- GitHub repository containing this code
- Telegram Bot Token (from @BotFather)

## Files added
- `Dockerfile`: Production container for python-telegram-bot v13.7
- `render.yaml`: Render blueprint to create a Web Service from Docker image

## Deploy Steps
1. Push your repository to GitHub.
2. In Render dashboard: New + → Blueprint → Select your repo.
3. Render will detect `render.yaml`. Review and create resources.
4. Configure Environment Variables on the created service:
   - `TELEGRAM_BOT_TOKEN` = your token (required)
   - `TZ` = Asia/Kolkata (optional)
5. Deploy. Render will build the Docker image and start the service.

## Runtime
- Command: `python -m bot.main`
- Long polling connects to Telegram and runs indefinitely.
- Auto-restart on failure is handled by Render.

## Logs
- Render console shows stdout/stderr from the bot.

## Common Issues
- Missing `TELEGRAM_BOT_TOKEN`: service will start but not connect. Set the env var and redeploy.
- Network egress restrictions: Ensure your Render plan allows outgoing traffic to Telegram.

## Local Test (optional)
```bash
docker build -t radhey-bot .
docker run --rm -e TELEGRAM_BOT_TOKEN=YOUR_TOKEN -e TZ=Asia/Kolkata radhey-bot
```

## Updates
- Commit and push; auto-deploy will rebuild and restart the bot.

