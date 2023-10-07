#!/bin/sh

cd /www/src

# make migrations (check if there are any changes in models)
poetry run python manage.py makemigrations
# migrate (apply changes to the database)
poetry run python manage.py migrate

# run gunicorn
poetry run gunicorn core.asgi:application --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker --reload
