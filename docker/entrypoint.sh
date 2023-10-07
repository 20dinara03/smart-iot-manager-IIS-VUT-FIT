#!/bin/sh

cd /www/src

# run django
poetry run python manage.py migrate

# run gunicorn
poetry run gunicorn core.asgi:application --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker
