<!-- frontend_deployment.md -->
<!-- Step-by-step reference for provisioning and deploying the Next.js frontend on the production VM. -->
<!-- Ensures future deploys to app.musicstudy.uk can be reproduced without missing setup steps. -->
# Next.js Frontend Deployment Guide

## 1. VM Preparation

- SSH into the Azure VM and install Node.js LTS (e.g., 20.x). If using NodeSource: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -` then `sudo apt-get install -y nodejs`.
- Choose a deployment root. Example assumes `~/music_frontend` with subfolders `releases/` and `shared/`.
- Ensure the VM user owns the directory (`sudo chown -R $USER:$USER ~/music_frontend`).
- Add `~/music_frontend/shared/.env.local` with at least `BACKEND_URL=https://samples.musicstudy.uk` so the frontend calls the live Django host.

## 2. First-Time Frontend Release

- Copy the repository’s `frontend/` directory (or a build artifact) to the VM. Place each release under `~/music_frontend/releases/<timestamp>/`.
- Point the `current` symlink at the release: `ln -sfn ~/music_frontend/releases/<timestamp> ~/music_frontend/current`.
- Install dependencies and build once:

  ```bash
  cd ~/music_frontend/current
  npm ci
  npm run build
  ```

- Keep `node_modules/` inside each release so the runtime resolves packages.

## 3. Runtime Process (PM2)

- Start the app with PM2 using the ecosystem config and persist the process list:

  ```bash
  cd ~/music_frontend/current
  pm2 start ecosystem.config.js
  pm2 save
  ```

- Useful commands: `pm2 status`, `pm2 logs music-frontend`, `pm2 restart music-frontend`.

## 4. Nginx Configuration

- Create `/etc/nginx/sites-available/app.musicstudy.uk` referencing the Next.js service:

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

- Symlink into `sites-enabled`, test (`sudo nginx -t`), then reload (`sudo systemctl reload nginx`).
- Issue HTTPS cert via certbot if needed: `sudo certbot --nginx -d app.musicstudy.uk`.

## 5. GitHub Actions / CI Updates

- Extend `.github/workflows/deploy.yml` so the `build` job also compiles the frontend:

  ```yaml
  - name: Set up Node
    uses: actions/setup-node@v4
    with:
      node-version: "20"
  - name: Install frontend dependencies
    working-directory: frontend
    run: npm ci
  - name: Build frontend
    working-directory: frontend
    run: npm run build
  - name: Archive frontend bundle
    run: |
      tar -czf frontend.tar.gz -C frontend .next package.json package-lock.json public ecosystem.config.js
  - name: Upload frontend artifact
    uses: actions/upload-artifact@v4
    with:
      name: frontend-build
      path: frontend.tar.gz
  ```

- In the `deploy` job, download the artifact and upload it to the VM before running scripts:

  ```yaml
  - name: Download frontend artifact
    uses: actions/download-artifact@v4
    with:
      name: frontend-build
  - name: Copy frontend bundle to server
    run: scp -i ~/.ssh/staging.key frontend.tar.gz deploy:~/music_frontend/releases/frontend.tar.gz
  ```

## 6. Deploy Script on VM

- Create `~/scripts/github_deploy_frontend.sh` to unpack and activate each release:

  ```bash
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
  cp ~/music_frontend/shared/.env.local .
  npm ci --omit=dev
  pm2 restart music-frontend || pm2 start ecosystem.config.js
  pm2 save
  ```

- Make the script executable (`chmod +x`) and call it from the deploy workflow after the Django script:

  ```yaml
  - name: Run frontend deployment script
    run: ssh deploy '${{ secrets.INSTALLATION_DIRECTORY }}/scripts/github_deploy_frontend.sh'
  - name: Restart nginx
    run: ssh deploy 'sudo systemctl reload nginx'
  ```

## 7. Smoke Testing

- Visit `https://app.musicstudy.uk/login` to confirm the frontend redirects correctly after sign-in.
- Verify API calls hit Django (`https://samples.musicstudy.uk`); watch logs (`pm2 logs`, `/var/log/nginx/app.musicstudy.uk.error.log`).
- Roll back by updating `~/music_frontend/current` to a previous timestamp and restarting PM2.

## 8. Ongoing Maintenance

- Keep Node.js and PM2 updated on the VM (`sudo apt upgrade`, `pm2 update`).
- Document any new environment variables in `shared/.env.local`.
- When ready to retire the legacy UI, redirect `samples.musicstudy.uk` or migrate routes incrementally to Next.js.
