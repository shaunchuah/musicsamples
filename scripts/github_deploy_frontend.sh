#!/bin/bash
# scripts/github_deploy_frontend.sh
# Automates rollout of a new Next.js release on the production VM using PM2.
# Keeps the live symlink and dependencies up to date before restarting the frontend service.

set -e

RELEASE_ROOT=~/music_frontend/releases
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TARGET="$RELEASE_ROOT/$TIMESTAMP"

mkdir -p "$TARGET"

tar -xzf "$RELEASE_ROOT/frontend.tar.gz" -C "$TARGET"
rm "$RELEASE_ROOT/frontend.tar.gz"

ln -sfn "$TARGET" ~/music_frontend/current

cd ~/music_frontend/current

cp ~/music_frontend/shared/.env.local .

npm ci --omit=dev

# Restart if the process exists, otherwise launch using the PM2 ecosystem config shipped with the release.
pm2 restart music-frontend || pm2 start ecosystem.config.js
pm2 save
