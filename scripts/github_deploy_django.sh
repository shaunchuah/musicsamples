#!/bin/bash

set -e

cd ~/musicsamples/
echo "Begin app update..."
echo "Activating python virtual environment..."
source ~/musicsamples/venv/bin/activate
echo "Installing requirements.txt..."
pip install -r requirements.txt
echo "Running migrations..."
python manage.py migrate
echo "Collecting static files..."
python manage.py collectstatic --noinput;
echo "Completed django deployment."
