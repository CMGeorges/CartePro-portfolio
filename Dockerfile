FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Flask config via env vars / .env (docker-compose)
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "60"]
