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

## 📋 Basic requirements

- [Django](https://www.djangoproject.com/)
- [Python](https://www.python.org/) 3.12+
- [SQLite](https://www.sqlite.org/) (for database)

## 🚀 Production requirements

- [Nginx](https://nginx.org/) (for production deployment)
- [Gunicorn](https://gunicorn.org/) (for WSGI HTTP server)
- [Redis](https://redis.io/) (for caching)
- AWS S3 (for file storage and backups)
- AWS SES (for email notifications)

## 🚦 Getting Started

To get a local copy up and running follow these steps. You need to have Python pre-installed on your machine. Rename `example.env` to `.env` to get development values set up.

## 🔧 Installation

### 1. Clone the repo

```sh
git clone https://github.com/shaunchuah/musicsamples.git
```

### 2. Setup a virtual environment for Django

```sh
cd musicsamples

# Create a virtual environment
python -m venv venv

source venv/bin/activate # for mac/linux
./venv/Scripts/activate # for windows

# Install required dependencies
pip install -r requirements.txt
```

### 3. Get Django up and running

First, copy the example.env file to .env and edit the values to suit your local development environment.

```sh
cp example.env .env
```

Edit the .env file with your desired values.

Run Django migrations, create superuser and startup the dev server:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Set up pre-commit hooks:

```sh
pre-commit install
```

## 📚 Documentation

G-Trac includes extensive documentation for both the system itself and research protocols.

### Orca Documentation

Run the following command to serve the Orca documentation locally:

```sh
mkdocs serve
```

The documentation will be available at <http://127.0.0.1:8080>

### Protocol Reference

G-Trac includes built-in protocol references for sample handling procedures including:

- EDTA plasma extraction
- cfDNA extraction
- Sample processing guidelines
- Haemolysis reference

These are accessible through the web interface under the reference section.

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

## 🏗️ Project Architecture

- app: main G-Trac sample tracking logic
- users: all authentication handling/views here
- datasets: frontend for orca data platform

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

## 📬 Contact

If you've used this to create something cool let me know about it!

X: [@drshaunchuah](https://x.com/drshaunchuah) \
Email: [shaun.chuah@glasgow.ac.uk](mailto:shaun.chuah@glasgow.ac.uk) \
Project Link: [https://github.com/shaunchuah/musicsamples](https://github.com/shaunchuah/musicsamples)
