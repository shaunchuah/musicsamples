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
echo "Collecting static files..."
python manage.py collectstatic --noinput;
echo "Completed django deployment."