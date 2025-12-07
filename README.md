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

For a full production runbook (VM prep, gunicorn/nginx configs, frontend runtime, backups, swap), use `production_deployment_guide.md`. Keep secrets out of git and copy any host-specific config into place manually.

Typical production stack:

- Ubuntu 24.04 with Python 3.12 and SQLite
- nginx reverse proxying to gunicorn for Django
- Redis for caching
- Node 20 + pnpm + pm2 for the Next.js frontend in `frontend/`
- AWS SES for transactional email; S3 or Azure Blob Storage for backups

Quick checklist if you need the short version:

1. Copy `example.env` to `.env` with production values (set `REDIS_URL`).
2. `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`.
3. Drop the sample gunicorn and nginx configs from `scripts/` into `/etc/systemd/system` and `/etc/nginx/sites-available`, enable them, and reload nginx.
4. Build the frontend in `frontend/` (`pnpm install && pnpm build`) and keep it alive with pm2; point nginx at the frontend service.
5. Set up a recurring backup of `production.sqlite3` using the helper scripts in `scripts/` and store credentials in a private file with `chmod 600`.

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
