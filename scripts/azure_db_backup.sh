#!/bin/bash

cd ~/musicsamples
cp production.sqlite3 ~/db_backups/$(date +%Y-%m-%d)_musicsamples_db.sqlite3
az storage azcopy blob upload -c gtrac-backups --account-name gutresearch -s ~/db_backups/$(date +%Y-%m-%d)_musicsamples_db.sqlite3 -d $(date +%Y-%m-%d)_musicsamples_db.sqlite3
rm ~/db_backups/$(date +%Y-%m-%d)_musicsamples_db.sqlite3
