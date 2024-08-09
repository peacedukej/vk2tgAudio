# vk_bot/Dockerfile
FROM python:3.10.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Команда для запуска vk_bot
CMD ["python", "-m", "connect"]
