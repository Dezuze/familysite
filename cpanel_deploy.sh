#!/bin/bash

# cPanel Rolling Release Deployment Script
# This script handles the "Poor Man's" Rolling Release strategy.

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
# Base directory where your app lives
APP_BASE="/home/$USER/www/family_app"
# Directory for all releases
RELEASES_DIR="$APP_BASE/releases"
# The live symlink that points to the current active release
LIVE_LINK="$APP_BASE/current"
# Format for release folder names
TIMESTAMP=$(date +%Y%m%d%H%M%S)
NEW_RELEASE_DIR="$RELEASES_DIR/$TIMESTAMP"

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------
mkdir -p "$RELEASES_DIR"
mkdir -p "$NEW_RELEASE_DIR"

echo "Deploying to $NEW_RELEASE_DIR..."

# -----------------------------------------------------------------------------
# COPY FILES
# -----------------------------------------------------------------------------
# Copy files from the current repository (cPanel Git repo root) to the new release folder
# Exclude git/node_modules/venv to keep it clean/fast
rsync -av --exclude '.git' --exclude 'node_modules' --exclude 'venv' --exclude '.venv' ./ "$NEW_RELEASE_DIR/"

# -----------------------------------------------------------------------------
# BACKEND SETUP
# -----------------------------------------------------------------------------
echo "Setting up Backend..."
cd "$NEW_RELEASE_DIR/Backend"

# Assuming a central virtualenv exists to save space/time, or create one per release.
# Using a shared venv is easier for cPanel Python App limits.
# UPDATE THIS PATH to your actual virtualenv path created by Setup Python App
VENV_PATH="/home/$USER/virtualenv/family_app_venv/3.10/bin/activate"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic --noinput
else
    echo "WARNING: Virtualenv not found at $VENV_PATH. Skipping Backend dependencies."
fi

# -----------------------------------------------------------------------------
# FRONTEND SETUP
# -----------------------------------------------------------------------------
echo "Setting up Frontend..."
cd "$NEW_RELEASE_DIR/Frontend"

# Use specific node version if needed, or rely on system
npm install
npm run build 
# For static site: npm run generate

# -----------------------------------------------------------------------------
# ACTIVATE RELEASE (Symlink Swap)
# -----------------------------------------------------------------------------
echo "Swapping symlinks..."
ln -sfn "$NEW_RELEASE_DIR" "$LIVE_LINK"

# -----------------------------------------------------------------------------
# RESTART SERVICES
# -----------------------------------------------------------------------------
# Touch the restart trigger for Passenger (Python)
mkdir -p "$LIVE_LINK/tmp"
touch "$LIVE_LINK/tmp/restart.txt"

# If using Node.js App selector, you might need to touch its restart file or rely on the symlink change being picked up (often requires manual restart or API call).
# For standard Passenger/Node, touching restart.txt works.
touch "$LIVE_LINK/Frontend/tmp/restart.txt" 2>/dev/null || true

echo "Deployment of release $TIMESTAMP complete!"
echo "Live site is now pointing to $NEW_RELEASE_DIR"

# -----------------------------------------------------------------------------
# CLEANUP
# -----------------------------------------------------------------------------
# Keep last 5 releases
cd "$RELEASES_DIR"
ls -dt * | tail -n +6 | xargs -r rm -rf --
