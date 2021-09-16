#!/bin/bash
cd ~/app/musicsamples/
echo "Begin app update..."
echo "Pulling from github..."
git pull
echo "Activating python virtual environment..."
source ~/app/env/bin/activate
echo "Collecting static files..."
python manage.py collectstatic --noinput;
echo "Restarting gunicorn..."
sudo systemctl restart gunicorn
echo "Restarting nginx..."
sudo systemctl restart nginx
echo "App update completed."
