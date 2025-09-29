#!/bin/bash
# scripts/github_deploy_frontend.sh
# Automates rollout of a new Next.js release on the production VM using PM2.
# Keeps the live symlink and dependencies up to date before restarting the frontend service.

set -e

echo "Starting frontend deployment script"

RELEASE_ROOT=~/music_frontend/releases
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TARGET="$RELEASE_ROOT/$TIMESTAMP"

echo "Creating target directory: $TARGET"
mkdir -p "$TARGET"

echo "Extracting frontend.tar.gz to $TARGET"
tar -xzf "$RELEASE_ROOT/frontend.tar.gz" -C "$TARGET"
rm "$RELEASE_ROOT/frontend.tar.gz"

echo "Updating current symlink"
ln -sfn "$TARGET" ~/music_frontend/current

echo "Symlink created: $(ls -la ~/music_frontend/current)"
if [ ! -d ~/music_frontend/current ]; then
  echo "Error: ~/music_frontend/current is not a directory"
  exit 1
fi

echo "Changing to current directory"
cd ~/music_frontend/current

# Source nvm and activate the specific Node version
source ~/.nvm/nvm.sh
nvm use v22.20.0

# Install dependencies and manage the PM2 process
npm ci --omit=dev
pm2 restart music_frontend || pm2 start ecosystem.config.js
pm2 save

echo "Files copied and deployed successfully"
