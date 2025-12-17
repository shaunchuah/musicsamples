<!-- production_deployment_guide_digitalocean.md -->
<!-- How to set up and deploy the Music Samples project on a fresh DigitalOcean droplet. -->
<!-- Exists to give operators a DigitalOcean-specific, copy-pasteable runbook for rebuilding prod end-to-end. -->

# G-Trac Production Deployment Guide (DigitalOcean)

Follow these steps on a fresh Ubuntu 24.04 droplet. Commands assume you start as `root`, create the `gtrac` user, and deploy to `/home/gtrac/musicsamples`. Use a login shell, keep secrets out of git, and `chmod 600` any secret files.

## 1) Droplet prep (run once as root, then switch to gtrac)

```bash
adduser --disabled-password --gecos "" gtrac
usermod -aG sudo gtrac
printf 'gtrac ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/gtrac
chmod 440 /etc/sudoers.d/gtrac
rsync --archive --chown=gtrac:gtrac /root/.ssh /home/gtrac
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip python3-dev libpq-dev build-essential git nginx redis-server certbot python3-certbot-nginx unzip
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
systemctl enable --now redis-server
# install azcopy
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
curl -L https://aka.ms/downloadazcopylinux64 -o azcopy.tar.gz
tar -xf azcopy.tar.gz
mv ./azcopy_linux_amd64_*/azcopy /usr/local/bin/azcopy
chmod +x /usr/local/bin/azcopy
azcopy --version
su - gtrac
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
cd /home/gtrac/musicsamples
sudo cp scripts/frontend_nginx_config /etc/nginx/sites-available/music-frontend
sudo ln -s /etc/nginx/sites-available/music-frontend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d app.musicstudy.uk
```

## 7) Backups to Azure and AWS S3 (as gtrac)

```bash
cp scripts/azure_db_backup.sh ~/azure_db_backup.sh && chmod +x ~/azure_db_backup.sh
cp scripts/aws_db_backup.sh ~/aws_db_backup.sh && chmod +x ~/aws_db_backup.sh
printf 'export AZURE_BACKUP_SAS_URL=YOUR_CONTAINER_SAS_URL_WITHOUT_QUERY\nexport AZURE_BACKUP_SAS_TOKEN=?YOUR_FULL_SAS_TOKEN\n' > ~/azure_backup_secrets
printf 'export AWS_BACKUP_BUCKET=your-s3-bucket\nexport AWS_BACKUP_PREFIX=musicsamples\nexport AWS_DEFAULT_REGION=us-east-1\nexport AWS_ACCESS_KEY_ID=your_access_key_id\nexport AWS_SECRET_ACCESS_KEY=your_secret_access_key\n' > ~/aws_backup_secrets
chmod 600 ~/azure_backup_secrets ~/aws_backup_secrets
mkdir -p ~/logs
(crontab -l; echo '0 2 * * * . ~/azure_backup_secrets && /bin/bash ~/azure_db_backup.sh >> ~/logs/azure_backup.log 2>&1') | crontab -
(crontab -l; echo '15 2 * * * . ~/aws_backup_secrets && /bin/bash ~/aws_db_backup.sh >> ~/logs/aws_backup.log 2>&1') | crontab -
```

## 8) CI/CD reconnect

- In GitHub repo settings, set secrets:
  - `PROD_SSH_USER=gtrac`
  - `PROD_SSH_HOST=<droplet-public-ip-or-domain>`
  - `PROD_SSH_KEY=<new private key>`
  - `INSTALLATION_DIRECTORY=/home/gtrac/musicsamples`
- Ensure `scripts/github_deploy_*.sh` are executable on the VM (`chmod +x`).
- Run a test deploy by pushing to main and watching GitHub Actions; verify services restart cleanly.

## 9) Validation

- Backend: `curl -I https://samples.musicstudy.uk` (expect 200); check `systemctl status gunicorn`.
- Redis: `redis-cli ping` (expect PONG).
- Frontend: `curl -I https://app.musicstudy.uk` (expect 200); load login/logout end-to-end.
- Optional local checks: `source venv/bin/activate && pytest && ruff format --check && ruff check`; in `frontend/`, run `pnpm lint && pnpm type-check && pnpm test && pnpm build`.
- Backup: run `/bin/bash ~/azure_db_backup.sh` and `/bin/bash ~/aws_db_backup.sh` once and confirm uploads.

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
