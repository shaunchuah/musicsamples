# G-Trac

G-Trac is an open source laboratory sample tracking and data management system created with [Django](https://www.djangoproject.com) to support translational biomedical research. Originally developed to track samples for the [MUSIC IBD Study](https://www.musicstudy.uk), it has evolved to serve as a frontend for our Orca data platform, providing researchers with unified access to clinical datasets.

## ✨ Key Features

- QR code-based sample tracking across multiple research sites
- Secure user authentication and role-based permissions
- Sample location management and movement tracking
- Protocol documentation and reference materials
- Data platform integration via the Orca interface
- Study-specific dataset access and management

## 🎯 Goals

1. Reduce time spent on sampling logistics
2. Provide a unified data access layer for researchers to access their data
3. Dynamic intelligence and analytics platform to direct future research efforts

## 🧰 Requirements

### Development

- Python 3.12+ (includes `pip` and SQLite on most systems)
- Django and supporting packages listed in `requirements.txt`
- SQLite (default development database)

### Production extras

- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- Redis (caching)
- AWS S3 (file storage and backups)
- AWS SES (transactional email)

## 🚦 Getting Started

Use the steps below to stand up a local development environment. Copy `example.env` to `.env` before you start so Django has sensible defaults.

### 1. Clone the repository

```sh
git clone https://github.com/shaunchuah/musicsamples.git
cd musicsamples
```

### 2. Create your environment

```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
./venv/Scripts/activate   # Windows PowerShell or CMD
pip install -r requirements.txt
cp example.env .env
```

Edit `.env` to match your local setup (database path, email settings, etc.).

### 3. Boot the application

```sh
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

### 4. (Optional) Enable local tooling

```sh
pre-commit install
```

## 🧪 Sample Management

### QR Codes

G-Trac uses QR codes for efficient sample tracking. The system supports:

- Bulk scanning of multiple samples
- Location updates via QR scanning
- Sample status tracking
- Integration with laboratory workflows

Cryogenic QR code labels were bulk printed from a label printing company and research samples were tagged at the point of collection and registered onto G-Trac. At specified receiving entrypoints to various lab workflows the samples were scanned in bulk to update their location (alternatively a status could be set into the location eg. "Departure Glasgow").

### Sample Processing

The system includes dedicated interfaces for:

- Adding new samples with metadata
- Updating sample locations
- Tracking sample movements between research sites
- Recording processing details such as freeze/thaw cycles

## 🌐 Deployment

You will need a domain name to deploy on. Configure the domain to point at your server.

The following would be a simple deployment for a small group onto a single server.

### Suggested Server Software Requirements

- Ubuntu 24.04
- Python
- SQLite
- Nginx
- Gunicorn
- Redis
- NVM, node, pnpm, pm2 (for Next.js frontend)
- AWS CLI or Azure CLI/azcopy (for database backups)

### External Service Dependency

- AWS Simple Email Service for transactional emails
- AWS S3 or Azure Storage for database backups

### Suggested production deployment

1. Ubuntu VPS (DigitalOcean, Linode, Lightsail etc. many options) - we use 24.04 LTS on Azure
2. Install python if required
3. Setup nginx and gunicorn (static requests through nginx, dynamic requests redirected to gunicorn serving Django). [Useful guide here](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04). Sample config files are in the scripts directory.
4. Set up an AWS account for transactional emails and S3.
5. Set up redis for caching - [https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04)
6. Clone the repo into a folder of your choice and remember to run:

   ```sh
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   ```

7. **Edit .env file to a production configuration**
8. Start up the whole stack and it should hopefully be working!
9. Set up SSL encryption on your server using letsencrypt
10. Edit `scripts/github_deploy_django.sh` and `.github/workflows/deploy.yml` to suit your server for automated deployments

### Next.js Frontend Deployment

The Next.js app lives in `frontend/` and serves `app.musicstudy.uk`. A typical production setup uses Node via `nvm`, installs dependencies with `pnpm`, and keeps the runtime alive with `pm2`.

1. Install Node with `nvm` (Node 20 LTS is a safe target) and ensure `pnpm` is available globally: `npm install -g pnpm`.
2. From `frontend/`, install dependencies and build once: `pnpm install && pnpm build`. Populate any required environment variables in `.env.production` (copy from `.env.example` if present).
3. Start the production server with pm2 so it survives restarts. A common pattern:

   ```sh
   pm2 start pnpm --name gtrac-frontend -- start
   pm2 save
   ```

   This runs `pnpm start`, binding to port 3000 by default.
4. Copy `scripts/frontend_nginx_config` to your server (for example `/etc/nginx/sites-available/app.musicstudy.uk`) and adjust certificate paths if needed. Symlink it into `sites-enabled` and reload nginx.
5. Keep the editable nginx file and any PM2 ecosystem configs outside this repository to avoid committing host-specific secrets or paths.

### Database Backups

The stack uses sqlite3 for ease of deployment. Copying the `production.sqlite3` file on a schedule is usually enough; a few helper scripts live in `scripts/`.

- `scripts/db_backup_example.sh` demonstrates a basic S3 upload.
- `scripts/azure_db_backup.sh` copies the database and uploads it to Azure Blob Storage with `azcopy`. Copy this script into your home directory (`cp scripts/azure_db_backup.sh ~/azure_db_backup.sh && chmod +x ~/azure_db_backup.sh`) so the executable sits outside the repo and avoids accidental commits. The script relies on two environment variables:
  - `AZURE_BACKUP_SAS_URL` – the SAS URL for the target container without any query string.
  - `AZURE_BACKUP_SAS_TOKEN` – the full SAS token beginning with `?`.

Store those exports in a private file (for example `~/azure_backup_secrets`), `chmod 600` it, and source it before the script runs so the credentials never live in the script itself:

```sh
. ~/azure_backup_secrets && /bin/bash ~/azure_db_backup.sh
```

#### Notes

1. Install the required CLI (AWS CLI or Azure CLI) on the host and authenticate once to ensure azcopy/boto have what they need to run.
2. `chmod +x` the backup script you intend to run.
3. Configure a cron job to source your secrets file and execute the script at the desired schedule. Example:

   ```sh
   0 2 * * * . ~/azure_backup_secrets && /bin/bash ~/azure_db_backup.sh >> ~/logs/azure_backup.log 2>&1
   ```

This samples the database nightly at 02:00 and logs the result; adjust paths and cadence as needed.

## 💾 Database Transfer

Use Django's dumpdata and loaddata as follows:

`python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > dump.json`

You will need to exclude contenttypes and auth.permission to switch between databases.

## 🔐 Specific Permission Settings

Once the app is deployed, make 4 groups - default, datasets, datastores, basic_science. For datasets, assign the view_dataset permission. For datastores, assign the view_datastore permission. For basic_science, assign the Add/change/delete/view basic science box permission. You can switch people back to the default group to remove access to datasets and datastores.

## 🐳 Orca Data Platform

G-Trac integrates with the Orca data platform, providing:

- Unified access to clinical datasets
- Study-specific data visualization
- Structured data dictionaries
- Data pipeline documentation

## ⚖️ License

Distributed under the MIT License.

## 👨‍⚕️ Author

Dr Shaun Chuah \
Clinical Senior Research Fellow \
School of Infection and Immunity \
University of Glasgow
X: [@drshaunchuah](https://x.com/drshaunchuah) \
Email: [shaun.chuah@glasgow.ac.uk](mailto:shaun.chuah@glasgow.ac.uk) \
