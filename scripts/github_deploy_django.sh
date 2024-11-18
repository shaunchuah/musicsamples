#!/bin/bash

set -e

cd ~/app/musicsamples/
echo "Begin app update..."
echo "Pulling from github..."
git pull || exit 1
echo "Activating python virtual environment..."
source ~/app/env/bin/activate
echo "Installing requirements.txt..."
pip install -r requirements.txt
# echo "Running migrations..."
# python manage.py migrate

# Temporary deployment to reset app migrations
echo "Resetting migrations..."
python manage.py showmigrations
python manage.py migrate --fake app zero
python manage.py showmigrations
python manage.py migrate --fake-initial
python manage.py showmigrations
# End temporary deployment fix

echo "Collecting static files..."
python manage.py collectstatic --noinput;
echo "Completed django deployment."