#!/bin/bash
set -e
RELEASE_ROOT=~/music_frontend/releases
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TARGET="$RELEASE_ROOT/$TIMESTAMP"
mkdir -p "$TARGET"
tar -xzf "$RELEASE_ROOT/frontend.tar.gz" -C "$TARGET"
rm "$RELEASE_ROOT/frontend.tar.gz"
ln -sfn "$TARGET" ~/music_frontend/current
cd ~/music_frontend/current
npm ci --omit=dev
pm2 restart music-frontend || pm2 start ecosystem.config.js
pm2 save
