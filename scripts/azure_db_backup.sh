#!/bin/bash

set -euo pipefail

# Expect the destination SAS pieces to be provided via environment variables.
: "${AZURE_BACKUP_SAS_URL:?Set AZURE_BACKUP_SAS_URL to the container SAS URL (no token)}"
: "${AZURE_BACKUP_SAS_TOKEN:?Set AZURE_BACKUP_SAS_TOKEN to the SAS token beginning with '?'}"

cd "${HOME}/musicsamples"

backup_dir="${HOME}/db_backups"
mkdir -p "${backup_dir}"

backup_date="$(date +%Y-%m-%d)"
backup_filename="${backup_date}_musicsamples_db.sqlite3"
local_backup_path="${backup_dir}/${backup_filename}"

cp production.sqlite3 "${local_backup_path}"

# Ensure the temporary copy is always removed, even if azcopy fails.
cleanup() {
  rm -f "${local_backup_path}"
}
trap cleanup EXIT

destination_base="${AZURE_BACKUP_SAS_URL%/}"
azcopy copy "${local_backup_path}" "${destination_base}/${backup_filename}${AZURE_BACKUP_SAS_TOKEN}"
