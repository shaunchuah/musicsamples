<!-- frontend_deployment.md -->
<!-- Step-by-step reference for provisioning and deploying the Next.js frontend on the production VM. -->
<!-- Ensures future deploys to app.musicstudy.uk can be reproduced without missing setup steps. -->
# Next.js Frontend Deployment Guide

## 1. VM Preparation

- SSH into the Azure VM and install Node.js 20.x with nvm.
- Install nvm if not present: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash`, refresh your shell (`source ~/.bashrc`), then run `nvm install 20`.
- Ensure PM2 is installed globally once (`npm install -g pm2`).
- Verify `pnpm` is available on the VM (`pnpm --version`). If not, enable it via corepack (`corepack enable pnpm`) or install it manually.
- Clone the repository into `$INSTALLATION_DIRECTORY` (same directory used for the Django deploy script). The deploy workflow already checks out the target commit there.
- Add any frontend environment variables to `$INSTALLATION_DIRECTORY/frontend/.env.production` or export them in the shell before starting PM2. The app defaults to the production backend URL if unset.

## 2. GitHub Actions Workflow

- `.github/workflows/deploy.yml` now keeps the frontend checks lightweight:

  ```yaml
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
        working-directory: frontend
      - run: pnpm run build
        working-directory: frontend
  ```

- The deploy job only needs the repository on the VM, so the artifact packaging, upload, and release directory juggling have been removed.

## 3. Deploy Script on the VM

- `scripts/github_deploy_frontend.sh` is executed over SSH after the Django deploy script. It reuses the checked-out repo, builds in place, prunes dev dependencies, and restarts PM2:

  ```bash
  #!/bin/bash
  set -euo pipefail
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  FRONTEND_DIR="$(dirname "$SCRIPT_DIR")/frontend"
  cd "$FRONTEND_DIR"
  source ~/.nvm/nvm.sh
  nvm use 20 || { nvm install 20 && nvm use 20; }
  pnpm install --frozen-lockfile
  pnpm run build
  pnpm prune --prod
  pm2 restart music-frontend || pm2 start ecosystem.config.js
  pm2 save
  ```

- Because the build happens on the VM, no tarball or rotating `~/music_frontend/releases` directories are needed. Rollbacks can be achieved by checking out an earlier commit and rerunning the script.

## 4. Nginx Configuration

- Continue to proxy traffic to the Next.js process with `/etc/nginx/sites-available/app.musicstudy.uk`:

  ```nginx
  server {
      server_name app.musicstudy.uk;

      location / {
          proxy_pass http://127.0.0.1:3000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

- Symlink into `sites-enabled`, test with `sudo nginx -t`, then reload via `sudo systemctl reload nginx`. Use certbot for HTTPS: `sudo certbot --nginx -d app.musicstudy.uk`.

## 5. Smoke Testing

- Visit `https://app.musicstudy.uk/login` and confirm the login flow works end-to-end.
- Monitor PM2 (`pm2 logs music-frontend`) and Nginx (`/var/log/nginx/app.musicstudy.uk.error.log`) for any immediate issues.
- To roll back, run `git checkout <previous_commit>` inside `$INSTALLATION_DIRECTORY`, then rerun the frontend deploy script.

## 6. Ongoing Maintenance

- Keep Node.js and PM2 updated on the VM (`nvm install --lts`, `pm2 update`).
- Document additional environment variables alongside the repository so future deploys remain reproducible.
- When the legacy UI is retired, ensure DNS and redirects continue to point users toward the Next.js frontend.
