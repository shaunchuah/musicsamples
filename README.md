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

### External Service Dependency

- AWS Simple Email Service for transactional emails
- AWS S3 Bucket for database backups

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

### Database Backups

The stack has been simplified to use sqlite3 for ease of deployment. Backup is simple as well, copy the db.sqlite3 file to S3 storage. An example script is included in `scripts/db_backup_example.sh`.

#### Notes

1. You will need to install either AWS CLI or Azure CLI and login from the server first.
2. Make the right backup script executable
3. Configure cron job to run the script at the desired time

To make the script executable:

```sh
chmod +x scripts/db_backup_example.sh
```

To configure a cron job:

```sh
crontab -e
```

Add the following line to the crontab file:

```sh
0 0 * * * /path/to/your/script/db_backup_example.sh
```

This copies production database to S3 at midnight every day

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

X: [@chershiong](https://x.com/chershiong) \
Email: [shaun.chuah@glasgow.ac.uk](mailto:shaun.chuah@glasgow.ac.uk) \
Project Link: [https://github.com/shaunchuah/musicsamples](https://github.com/shaunchuah/musicsamples)
