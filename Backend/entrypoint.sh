#!/bin/sh

# Wait for DB if needed (can add logic here)

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
