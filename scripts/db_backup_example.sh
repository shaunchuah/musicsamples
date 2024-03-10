#!/bin/bash
# Add PGPASSWORD here before using

PGPASSWORD='' pg_dump -U postgres -h localhost -Fc sampletrek > ~/db_backups/$(date +%Y-%m-%d_%H-%M-%S)_musicsamples_db_data.sql
PGPASSWORD='' pg_dumpall -U postgres -h localhost -g > ~/db_backups/$(date +%Y-%m-%d_%H-%M-%S)_musicsamples_globals.sql
