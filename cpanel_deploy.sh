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

# Try to find the virtualenv path from an environment variable or default
# In cPanel, this is typically /home/USER/virtualenv/APP_NAME/PYTHON_VERSION/bin/activate
VENV_PATH="${PYTHON_VENV_PATH:-/home/$USER/virtualenv/family_app_venv/3.13/bin/activate}"

if [ -f "$VENV_PATH" ]; then
    echo "Activating virtualenv at $VENV_PATH..."
    source "$VENV_PATH" || { echo "ERROR: Failed to source $VENV_PATH"; exit 1; }
    pip install --upgrade pip
    pip install -r requirements.txt || { echo "ERROR: Failed to install backend requirements"; exit 1; }
    python manage.py migrate || { echo "ERROR: Database migration failed"; exit 1; }
    python manage.py collectstatic --noinput || { echo "ERROR: Collectstatic failed"; exit 1; }
else
    echo "WARNING: Virtualenv not found at $VENV_PATH. Skipping Backend dependencies."
fi

# -----------------------------------------------------------------------------
# FRONTEND SETUP
# -----------------------------------------------------------------------------
echo "Setting up Frontend..."
cd "$NEW_RELEASE_DIR/Frontend"

# Ensure we are using a stable node version if available via NVM or similar, 
# otherwise rely on the cPanel Node setup which usually handles this.
npm install --legacy-peer-deps || { echo "ERROR: npm install failed"; exit 1; }
npm run build || { echo "ERROR: npm build failed"; exit 1; }

# -----------------------------------------------------------------------------
# ACTIVATE RELEASE (Symlink Swap)
# -----------------------------------------------------------------------------
echo "Swapping symlinks..."
ln -sfn "$NEW_RELEASE_DIR" "$LIVE_LINK"

# -----------------------------------------------------------------------------
# RESTART SERVICES
# -----------------------------------------------------------------------------
# Restart Backend (Passenger)
mkdir -p "$LIVE_LINK/Backend/tmp"
touch "$LIVE_LINK/Backend/tmp/restart.txt"

# Restart Frontend (Passenger/Node)
mkdir -p "$LIVE_LINK/Frontend/tmp"
touch "$LIVE_LINK/Frontend/tmp/restart.txt"

echo "Deployment of release $TIMESTAMP complete!"
echo "Live site is now pointing to $NEW_RELEASE_DIR"

# -----------------------------------------------------------------------------
# CLEANUP
# -----------------------------------------------------------------------------
# Keep last 5 releases
cd "$RELEASES_DIR"
ls -dt * | tail -n +6 | xargs -r rm -rf --
