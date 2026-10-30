#!/bin/sh

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Generate celebration posters for today on startup
echo "Generating daily celebration posters..."
python manage.py generate_daily_posters || true

exec "$@"
