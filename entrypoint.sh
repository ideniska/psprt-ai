#!/bin/bash

python manage.py migrate --noinput
#gunicorn project.wsgi:application --bind 0.0.0.0:8000 --reload
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000