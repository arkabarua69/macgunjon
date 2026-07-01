FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=macgunjon.settings
ENV GUNICORN_WORKERS=4
ENV SECRET_KEY=build-time-key-do-not-use-in-production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 libffi-dev \
    libcairo2 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

EXPOSE 8000

CMD gunicorn macgunjon.wsgi:application --bind 0.0.0.0:8000 --workers $GUNICORN_WORKERS --timeout 120
