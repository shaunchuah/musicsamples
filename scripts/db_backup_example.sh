#!/bin/bash
# Add PGPASSWORD here before using

PGPASSWORD='' pg_dump -U postgres -h localhost -Fc sampletrek > ~/db_backups/sampletrek_db_backup_$(date +%d-%m-%Y_%H-%M-%S).sql
PGPASSWORD='' pg_dumpall -U postgres -h localhost -g > ~/db_backups/sampletrek_db_globals_backup_$(date +%d-%m-%Y_%H-%M-%S).sql
