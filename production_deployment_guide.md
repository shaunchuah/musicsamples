<!-- production_deployment_guide.md -->
<!-- How to set up and deploy the Music Samples project on a fresh production VM. -->
<!-- Exists to give operators a single, copy-pasteable runbook for rebuilding prod end-to-end. -->

# G-Trac Production Deployment Guide

Follow these steps on a fresh Ubuntu 24.04 VM. Commands assume deploy user `gtrac` and repo at `/home/gtrac/musicsamples`. Use a login shell, keep secrets out of git, and `chmod 600` any secret files.

## 1) VM prep (run once as root, then switch to gtrac)

```bash
sudo adduser gtrac && sudo usermod -aG sudo gtrac
sudo rsync --archive --chown=gtrac:gtrac ~/.ssh /home/gtrac
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip python3-dev libpq-dev build-essential git nginx redis-server certbot python3-certbot-nginx unzip
sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw --force enable
sudo systemctl enable --now redis-server
# install azcopy
cd /tmp
curl -L https://aka.ms/downloadazcopylinux64 -o azcopy.tar.gz
tar -xf azcopy.tar.gz
sudo mv ./azcopy_linux_amd64_*/azcopy /usr/local/bin/azcopy
sudo chmod +x /usr/local/bin/azcopy
azcopy --version
```

## 2) Clone and configure backend (as gtrac)

```bash
cd /home/gtrac
git clone https://github.com/shaunchuah/musicsamples.git musicsamples
cd musicsamples
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
cp example.env .env  # edit with production values; set REDIS_URL=redis://127.0.0.1:6379/0
chmod 600 .env
python manage.py migrate
python manage.py collectstatic --noinput
```

## 3) Systemd for gunicorn (as root)

```bash
sudo cp scripts/gunicorn.service /etc/systemd/system/gunicorn.service
sudo cp scripts/gunicorn.socket /etc/systemd/system/gunicorn.socket
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.socket
sudo systemctl status gunicorn
```

## 4) nginx for backend (as root)

```bash
sudo cp scripts/musicsamples_nginx_config /etc/nginx/sites-available/musicsamples
sudo ln -s /etc/nginx/sites-available/musicsamples /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d samples.musicstudy.uk
```

## 5) Frontend runtime (as gtrac)

```bash
# install nvm (as gtrac)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 20 && nvm use 20
npm install -g pnpm pm2
cd ~/musicsamples/frontend
printf 'BACKEND_URL=https://samples.musicstudy.uk\n' > .env.production
chmod 600 .env.production
pnpm install --frozen-lockfile
pnpm build
pm2 start ecosystem.config.js --name music-frontend
pm2 save
pm2 startup systemd -u gtrac --hp /home/gtrac  # run the printed sudo command once
```

## 6) nginx for frontend (as root)

```bash
sudo cp scripts/frontend_nginx_config /etc/nginx/sites-available/music-frontend
sudo ln -s /etc/nginx/sites-available/music-frontend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d app.musicstudy.uk
```

## 7) Backups (as gtrac)

```bash
cp scripts/azure_db_backup.sh ~/azure_db_backup.sh && chmod +x ~/azure_db_backup.sh
printf 'export AZURE_BACKUP_SAS_URL=YOUR_CONTAINER_SAS_URL_WITHOUT_QUERY\nexport AZURE_BACKUP_SAS_TOKEN=?YOUR_FULL_SAS_TOKEN\n' > ~/azure_backup_secrets
chmod 600 ~/azure_backup_secrets
mkdir -p ~/logs
(crontab -l; echo '0 2 * * * . ~/azure_backup_secrets && /bin/bash ~/azure_db_backup.sh >> ~/logs/azure_backup.log 2>&1') | crontab -
```

## 8) CI/CD reconnect

- In GitHub repo settings, set secrets:
  - `PROD_SSH_USER=gtrac`
  - `PROD_SSH_HOST=<vm-public-ip-or-domain>`
  - `PROD_SSH_KEY=<new private key>`
  - `INSTALLATION_DIRECTORY=/home/gtrac/musicsamples`
- Ensure `scripts/github_deploy_*.sh` are executable on the VM (`chmod +x`).
- Run a test deploy by pushing to main and watching GitHub Actions; verify services restart cleanly.

## 9) Validation

- Backend: `curl -I https://samples.musicstudy.uk` (expect 200); check `systemctl status gunicorn`.
- Redis: `redis-cli ping` (expect PONG).
- Frontend: `curl -I https://app.musicstudy.uk` (expect 200); load login/logout end-to-end.
- Optional local checks: `source venv/bin/activate && pytest && ruff format --check && ruff check`; in `frontend/`, run `pnpm lint && pnpm type-check && pnpm test && pnpm build`.
- Backup: run `/bin/bash ~/azure_db_backup.sh` once and confirm blob upload.

## 10) Swapfile (as root) — set 4G swap to reduce OOM risk

```bash
sudo swapoff -a
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
swapon --show  # verify 4.0G active
```
