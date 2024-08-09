# fast_api/Dockerfile

FROM python:3.10.9

WORKDIR /app

COPY /requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Временная команда для проверки содержимого рабочей директории
# RUN cd /app

# Открываем порт 8000 для FastAPI
EXPOSE 9000

# Команда для запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload", "--log-level", "debug"]
