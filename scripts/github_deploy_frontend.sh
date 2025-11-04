#!/bin/bash
# scripts/github_deploy_frontend.sh
# Automates rollout of a new Next.js release on the production VM using PM2.
# Builds in-place from the checked-out repository before restarting the frontend service.

set -euo pipefail

echo "Starting frontend deployment script"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Error: frontend directory not found at $FRONTEND_DIR"
  exit 1
fi

echo "Changing to frontend directory"
cd "$FRONTEND_DIR"

source ~/.nvm/nvm.sh
if ! nvm use 20 >/dev/null 2>&1; then
  echo "Installing Node.js 20 via nvm"
  nvm install 20
  nvm use 20
else
  echo "Using Node.js $(node --version)"
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "Error: pnpm is not installed or not on PATH."
  exit 1
fi

echo "Installing dependencies with pnpm"
pnpm install --frozen-lockfile

echo "Building production bundle"
pnpm run build

echo "Removing development dependencies"
pnpm prune --prod

echo "Restarting frontend process with PM2"
pm2 restart music-frontend || pm2 start ecosystem.config.js
pm2 save

echo "Frontend deployment completed successfully"
