# G-Trac

G-Trac started as an open source sample tracking system created with [Django](https://www.djangoproject.com) to support translational research in Scotland. As of end-2024, we are using it as a frontend for our Orca data platform.

## Goals

1. Reduce time spent on sampling logistics
2. Provide a unified data access layer for researchers to access their data
3. Dynamic intelligence and analytics platform to direct future research efforts

## About The Project

### Tracking of 30,000 research samples across multiple sites and labs

G-Trac was developed to solve the problem of tracking 30,000 research samples across multiple study sites with multiple laboratory endpoints. In our use we deployed it on a single droplet/virtual private server hosted by DigitalOcean and used Amazon Web Services for handling email and database backups. Code was deployed using github and this allowed rapid deployment of new features as the need arose. Check out the study here: [MUSIC IBD Study](https://www.musicstudy.uk)

### QR code labelling

Cryogenic QR code labels were bulk printed from a label printing company and research samples were tagged at the point of collection and registered onto G-Trac. At specified receiving entrypoints to various lab workflows the samples were scanned in bulk to update their location (alternatively a status could be set into the location eg. "Departure Glasgow").

## Requirements

- [Django](https://www.djangoproject.com/)
- [Python 3.12](https://www.python.org/)

## Getting Started

To get a local copy up and running follow these steps. You need to have Python pre-installed on your machine. Rename `example.env` to `.env` to get development values set up.

## Installation

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

### 4. Orca Documentation

To view Orca documentation, you can use the following command:

```sh
mkdocs serve
```

## Deployment

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

1. Ubuntu VPS (DigitalOcean, Linode, Lightsail etc. many options) - we use 24.04 LTS on DigitalOcean, comes with Python 3.12 installed already
2. Install python if required
3. Setup nginx and gunicorn (static requests through nginx, dynamic requests redirected to gunicorn serving Django). [Useful guide here](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04). Sample config files are in the scripts directory.
4. Set up an AWS account for transactional emails and S3.
5. Set up redis for caching - [https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04))
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

As a side note, you will need to make the scripts executable and configure a cron job to run the scripts.

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

## Database Transfer

Use Django's dumpdata and loaddata as follows:

`python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > dump.json`

You will need to exclude contenttypes and auth.permission to switch between databases.

## Project Architecture

- app: main G-Trac sample tracking logic
- users: all authentication handling/views here
- datasets: frontend for orca data platform

## License

Distributed under the MIT License.

## Author

Dr Shaun Chuah \
Clinical Senior Research Fellow \
School of Infectiona and Immunity \
University of Glasgow

## Contact

If you've used this to create something cool let me know about it!

Twitter: [@chershiong](https://twitter.com/chershiong) \
Email: [shaun.chuah@glasgow.ac.uk](mailto:shaun.chuah@glasgow.ac.uk) \
Project Link: [https://github.com/shaunchuah/musicsamples](https://github.com/shaunchuah/musicsamples)
