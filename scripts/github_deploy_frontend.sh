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

NPM_BIN=$(command -v npm)
PM2_BIN=$(command -v pm2)

if [[ -z "$NPM_BIN" ]]; then
  echo "npm not found on PATH." >&2
  exit 127
fi

if [[ -z "$PM2_BIN" ]]; then
  echo "pm2 not found on PATH." >&2
  exit 127
fi

echo "Installing dependencies"
"$NPM_BIN" ci --omit=dev

echo "Restarting or starting PM2 process"
# Restart if the process exists, otherwise launch using the PM2 ecosystem config shipped with the release.
"$PM2_BIN" restart music-frontend || "$PM2_BIN" start ecosystem.config.js
"$PM2_BIN" save

echo "Deployment completed successfully"
