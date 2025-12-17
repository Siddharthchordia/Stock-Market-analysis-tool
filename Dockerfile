FROM python:3.12-slim

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip 

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py crontab remove && python manage.py crontab add && cron && python manage.py runserver 0.0.0.0:8000"]
