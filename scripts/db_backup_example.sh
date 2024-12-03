#!/bin/bash

cd ~/musicsamples
cp production.sqlite3 ~/db_backups/$(date +%Y-%m-%d_%H-%M-%S)_musicsamples_db.sqlite3
aws s3 sync ~/db_backups s3://musicsamplesdbbackup
