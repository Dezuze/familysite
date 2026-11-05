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

# Ensure 27th Kudumbayogam celebration news and photos are present
echo "Seeding 27th Kudumbayogam news post..."
python manage.py add_kudumbayogam_27_news || true

exec "$@"
