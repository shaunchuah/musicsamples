<!-- codex/plans/redeploy.md -->
<!-- Step-by-step ExecPlan to rebuild and redeploy the Music Samples stack on a fresh Azure Ubuntu 24.04 VM. -->
<!-- Exists to give a novice everything needed to stand the system back up after the compromised server was terminated. -->

# Rebuild and Redeploy Music Samples on Azure Ubuntu 24.04

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this plan in accordance with `codex/PLANS.md`.

## Purpose / Big Picture

Recreate the full production deployment on a new Azure Ubuntu 24.04 LTS VM after the previous host was compromised. The goal is to stand up the Django backend (served by gunicorn behind nginx) and the Next.js frontend (served by pm2 behind nginx), restore environment configuration, and re-enable backups and CI/CD deploys. Success means users can reach the backend at the production domain, the frontend at its domain, authentication works, and automated backups plus deployments are running safely on the new VM.

## Progress

- [x] (2025-12-07 14:06Z) Authored initial redeployment ExecPlan based on current repository scripts and configs.
- [x] (2025-12-07 14:15Z) Set deployment user to `gtrac` for VM setup, service ownership, and CI/CD secrets.
- [ ] Prepare Azure VM networking, DNS, and base packages.
- [ ] Provision backend runtime (Python virtualenv, systemd gunicorn) and nginx for Django.
- [ ] Provision frontend runtime (Node via nvm, pnpm, pm2) and nginx for Next.js.
- [ ] Wire environment secrets, storage, email, and Redis.
- [ ] Enable backups to Azure Storage and validate restore path.
- [ ] Reconnect GitHub Actions deploy workflow to the new VM and validate end-to-end rollouts.
- [ ] Final verification, hardening, and retrospective.

## Surprises & Discoveries

- psycopg2-binary fails to build without PostgreSQL client headers on Ubuntu 24.04; install `python3-dev` and `libpq-dev` before `pip install -r requirements.txt`.
- Redis is installed locally via `redis-server`; point `REDIS_URL` to `redis://127.0.0.1:6379/0` in `.env` and ensure the service is running.

## Decision Log

- None yet. Log choices such as filesystem layout, system user names, nginx hostnames, and whether to reuse existing CI/CD secrets.
- Decision: Use system user `gtrac` for all deployment steps on the new VM.
  Rationale: Aligns with existing gunicorn service template paths and keeps ownership consistent.
  Date/Author: 2025-12-07 / Codex agent

## Outcomes & Retrospective

- To be populated after the new environment is live. Summarize what worked, what needed changes, and any remaining risks.

## Context and Orientation

Repository structure relevant to deployment:
- Django backend at the repo root (`manage.py`, `config/settings.py`), served via gunicorn; static assets collected to `staticfiles/`.
- Next.js 15 frontend in `frontend/` with PM2 config in `frontend/ecosystem.config.js`; uses pnpm and Node 20.
- Deployment helpers: `scripts/github_deploy_django.sh` (pip install, migrate, collectstatic), `scripts/github_deploy_frontend.sh` (pnpm install/build, pm2 restart), nginx sample `scripts/musicsamples_nginx_config` (backend) and `scripts/frontend_nginx_config` (frontend), systemd unit templates `scripts/gunicorn.service` and `scripts/gunicorn.socket`.
- CI/CD: `.github/workflows/deploy.yml` pushes via SSH to run the above scripts and restart services.
- Environment template: `example.env` for backend; frontend expects `.env.production` with `BACKEND_URL`.
- Backups: `scripts/azure_db_backup.sh` copies SQLite DB to Azure Blob Storage using `AZURE_BACKUP_SAS_URL` and `AZURE_BACKUP_SAS_TOKEN`.

Assumptions:
- You will deploy to a new Azure VM (Ubuntu 24.04 LTS) with the sudo user `gtrac` and SSH key access.
- Domains: backend `samples.musicstudy.uk`, frontend `app.musicstudy.uk`.
- SQLite remains the database; no database schema changes are performed beyond running migrations that correspond to committed code.

## Plan of Work

Rebuild proceeds in clear stages to minimize downtime and risk:
1) Harden the new VM and prepare networking: create a sudo user, add SSH keys, configure the Azure NSG to allow 22/80/443 only, and set DNS records to the new public IP when ready. Enable ufw with minimal rules and ensure time sync is active.
2) Install base dependencies: Python 3.12+, `python3-venv`, `pip`, `build-essential`, `git`, `nginx`, `redis-server`, `certbot` + `python3-certbot-nginx`, and Azure CLI (for backups). Keep package installs minimal; avoid starting services until configs exist.
3) Fetch the code: clone the repository into `/home/<user>/musicsamples` and ensure ownership by the deploy user. Copy `example.env` to `.env` and populate production secrets (SECRET_KEY, email, Redis URL, storage, etc.). Keep secrets outside git and lock permissions (`chmod 600 .env`).
4) Backend runtime: create a Python virtualenv in the repo (`python -m venv venv`), activate, upgrade pip, and `pip install -r requirements.txt`. Run `python manage.py migrate` and `python manage.py collectstatic --noinput`. Define systemd units based on `scripts/gunicorn.service` and `scripts/gunicorn.socket`, updating paths to `/home/<user>/musicsamples` and the correct virtualenv bin. Enable and start the socket/service.
5) Frontend runtime: install nvm for the deploy user, install Node 20 LTS, install pnpm globally, then in `frontend/` run `pnpm install --frozen-lockfile && pnpm build`. Ensure `.env.production` is set with `BACKEND_URL=https://<backend-domain>`. Start via `pm2 start ecosystem.config.js`, name the process (e.g., `music-frontend`), and `pm2 save && pm2 startup systemd` to persist.
6) Web server: place nginx site configs based on `scripts/musicsamples_nginx_config` (backend) and `scripts/frontend_nginx_config` (frontend). Update `server_name` entries, SSL certificate paths, and upstream sockets/ports (backend via `/run/gunicorn.sock`, frontend default `localhost:3000`). Enable sites, test config (`nginx -t`), and reload. Use certbot to obtain and renew TLS certificates (`certbot --nginx -d <domain>`).
7) Backups: copy `scripts/azure_db_backup.sh` to the deploy user’s home, `chmod +x`, and create `~/azure_backup_secrets` exporting `AZURE_BACKUP_SAS_URL` and `AZURE_BACKUP_SAS_TOKEN`. Add a cron entry to source secrets and run the script (e.g., nightly). Store logs in `~/logs/azure_backup.log`.
8) CI/CD reconnect: update GitHub Secrets (`PROD_SSH_USER`, `PROD_SSH_KEY`, `PROD_SSH_HOST`, `INSTALLATION_DIRECTORY`) to point at the new VM and path. Verify the workflow still fits the new systemd service name if changed and that deployment scripts are executable.
9) Validation and hardening: run backend tests and lint locally if desired (`pytest`, `ruff format --check && ruff check`), check frontend build (`pnpm lint`, `pnpm type-check`, `pnpm test`, `pnpm build`). On the VM, exercise health: `curl -I https://<backend-domain>` for 200, login/logout via frontend, confirm static assets served, and verify Redis connectivity. Harden by trimming sudoers, disabling root SSH, enabling automatic security updates, and ensuring ufw permits only required ports.
10) Document outcomes: update this plan’s Progress, Decision Log, and Surprises sections with actual paths, service names, and any deviations, then summarize in Outcomes & Retrospective.

## Concrete Steps

Commands assume user `gtrac`, repo at `/home/gtrac/musicsamples`. Run all commands in a login shell on the VM unless noted. Do not paste secrets into shell history; use a secrets file with `chmod 600`.

1) VM prep (as root once, then switch to deploy):
    sudo adduser gtrac && sudo usermod -aG sudo gtrac
    sudo rsync --archive --chown=gtrac:gtrac ~/.ssh /home/gtrac
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-venv python3-pip python3-dev libpq-dev build-essential git nginx redis-server certbot python3-certbot-nginx unzip
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash   # for backups
    sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw --force enable
    sudo systemctl enable --now redis-server
    # install azcopy
    cd /tmp
    curl -L https://aka.ms/downloadazcopylinux64 -o azcopy.tar.gz
    tar -xf azcopy.tar.gz
    sudo mv ./azcopy_linux_amd64_*/azcopy /usr/local/bin/azcopy
    sudo chmod +x /usr/local/bin/azcopy
    azcopy --version

2) Clone and configure backend (as gtrac in `/home/gtrac`):
    git clone https://github.com/shaunchuah/musicsamples.git musicsamples
    cd musicsamples
    python3 -m venv venv && source venv/bin/activate
    pip install --upgrade pip && pip install -r requirements.txt
    cp example.env .env  # then edit with production values; set REDIS_URL=redis://127.0.0.1:6379/0; chmod 600 .env
    python manage.py migrate
    python manage.py collectstatic --noinput

3) Systemd for gunicorn (as root):
    sudo cp scripts/gunicorn.service /etc/systemd/system/gunicorn.service
    sudo cp scripts/gunicorn.socket /etc/systemd/system/gunicorn.socket
    sudo sed -i 's#/home/gtrac#/home/gtrac/musicsamples#g' /etc/systemd/system/gunicorn.service
    sudo sed -i 's#/home/trac/venv#/home/gtrac/musicsamples/venv#g' /etc/systemd/system/gunicorn.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now gunicorn.socket
    sudo systemctl status gunicorn

4) nginx for backend:
    sudo cp scripts/musicsamples_nginx_config /etc/nginx/sites-available/musicsamples
    sudo sed -i 's/samples.musicstudy.uk/samples.musicstudy.uk/g' /etc/nginx/sites-available/musicsamples
    sudo ln -s /etc/nginx/sites-available/musicsamples /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    sudo certbot --nginx -d samples.musicstudy.uk

5) Frontend runtime (as gtrac):
    # install nvm (run as gtrac, not root)
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install 20 && nvm use 20
    npm install -g pnpm pm2
    cd ~/musicsamples/frontend
    cp .env.local .env.production  # or create fresh; set BACKEND_URL=https://samples.musicstudy.uk
    pnpm install --frozen-lockfile
    pnpm build
    pm2 start ecosystem.config.js --name music-frontend
    pm2 save
    pm2 startup systemd -u gtrac --hp /home/gtrac

6) nginx for frontend:
    sudo cp scripts/frontend_nginx_config /etc/nginx/sites-available/music-frontend
    sudo sed -i 's/app.musicstudy.uk/app.musicstudy.uk/g' /etc/nginx/sites-available/music-frontend
    sudo ln -s /etc/nginx/sites-available/music-frontend /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    sudo certbot --nginx -d app.musicstudy.uk

7) Backups (as gtrac):
    cp scripts/azure_db_backup.sh ~/azure_db_backup.sh && chmod +x ~/azure_db_backup.sh
    # create secrets file with SAS URL (no query string) and SAS token (starts with ?)
    printf 'export AZURE_BACKUP_SAS_URL=YOUR_CONTAINER_SAS_URL_WITHOUT_QUERY\nexport AZURE_BACKUP_SAS_TOKEN=?YOUR_FULL_SAS_TOKEN\n' > ~/azure_backup_secrets
    chmod 600 ~/azure_backup_secrets
    (crontab -l; echo '0 2 * * * . ~/azure_backup_secrets && /bin/bash ~/azure_db_backup.sh >> ~/logs/azure_backup.log 2>&1') | crontab -

8) CI/CD reconnect:
    In GitHub repo settings, set secrets:
      PROD_SSH_USER=gtrac
      PROD_SSH_HOST=<vm-public-ip-or-domain>
      PROD_SSH_KEY=<new private key>
      INSTALLATION_DIRECTORY=/home/gtrac/musicsamples
    Ensure `scripts/github_deploy_*.sh` are executable on the VM (`chmod +x`). Run a test deploy by pushing to main and watching the GitHub Actions logs; verify services restart cleanly.

9) Validation:
    Backend: curl -I https://samples.musicstudy.uk (expect 200), check `systemctl status gunicorn`.
    Redis: run `redis-cli ping` (expect PONG) to confirm local cache availability.
    Frontend: curl -I https://app.musicstudy.uk (expect 200) and load login page. Confirm login/logout works end-to-end.
    Optional local checks before deploy: `source venv/bin/activate && pytest && ruff format --check && ruff check`; in `frontend/`, run `pnpm lint && pnpm type-check && pnpm test && pnpm build`.
    Backup: run `/bin/bash ~/azure_db_backup.sh` once manually and confirm blob appears in the target container.

## Validation and Acceptance

Deployment is accepted when:
- HTTPS responds for both backend and frontend domains with valid certificates.
- Django serves API and static assets via gunicorn+nginx; `systemctl status gunicorn` shows active.
- Next.js app serves via PM2 and nginx; `pm2 status music-frontend` shows online.
- Redis is reachable and configured via `.env` (if used); no connection errors in logs.
- Backup script successfully uploads the SQLite DB to Azure Blob and cron entry exists.
- GitHub Actions deploy workflow completes successfully and updates both backend and frontend on the VM.

## Idempotence and Recovery

- Package installs and service setup are safe to re-run; `pip install` and `pnpm install` are idempotent. Rerunning `collectstatic` and `migrate` is safe against existing state.
- If nginx or systemd reloads fail, inspect `/var/log/nginx/error.log` or `journalctl -u gunicorn` and fix paths/domains before retrying.
- If PM2 fails to start, run `pm2 logs music-frontend` and ensure Node version and env vars are correct; you can delete and recreate the process.
- Keep backups of `.env` and `azure_backup_secrets`; if lost, redeploying will fail. Avoid storing secrets in git or shell history.

## Artifacts and Notes

- Service units: `/etc/systemd/system/gunicorn.service` and `/etc/systemd/system/gunicorn.socket` derived from `scripts/`.
- nginx sites: `/etc/nginx/sites-available/musicsamples` (backend) and `/etc/nginx/sites-available/music-frontend` (frontend) symlinked into `sites-enabled/`.
- Backup script: `~/azure_db_backup.sh` and cron entry for nightly runs; logs at `~/logs/azure_backup.log`.
- CI/CD: `.github/workflows/deploy.yml` orchestrates tests/builds then SSH deploy using the above scripts.

## Interfaces and Dependencies

- Backend interface: WSGI app `config.wsgi:application` served via gunicorn, UNIX socket `/run/gunicorn.sock` proxied by nginx. Requires Python 3.12+, Django per `requirements.txt`, Redis (for caching), AWS SES/S3 or Azure storage if configured via `.env`.
- Frontend interface: Next.js app started with `pnpm start` through PM2 as configured in `frontend/ecosystem.config.js`; nginx proxies HTTPS traffic to port 3000. Depends on Node 20, pnpm, pm2, and `.env.production` containing `BACKEND_URL`.
- Backup dependency: Azure Blob Storage SAS URL/token, Azure CLI/azcopy present on host.

Note: Update this plan with actual values, deviations, and verification outputs as you progress. Keep it self-contained so a new contributor can rebuild the environment from scratch.
