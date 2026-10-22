#!/bin/sh
set -e
python manage.py migrate --noinput
# Into the volume nginx serves /static/ from.
python manage.py collectstatic --noinput --clear
python manage.py seed_demo
exec "$@"
