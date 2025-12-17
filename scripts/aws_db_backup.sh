# scripts/aws_db_backup.sh
# Uploads the production sqlite backup to an AWS S3 bucket.
# Exists to provide a simple, repeatable S3 backup run for cron.
#!/bin/bash

set -euo pipefail

# Expect AWS credentials and destination to be provided via environment variables.
: "${AWS_BACKUP_BUCKET:?Set AWS_BACKUP_BUCKET to the S3 bucket name}"
: "${AWS_DEFAULT_REGION:?Set AWS_DEFAULT_REGION to the AWS region (for example, us-east-1)}"
: "${AWS_ACCESS_KEY_ID:?Set AWS_ACCESS_KEY_ID for the backup IAM user}"
: "${AWS_SECRET_ACCESS_KEY:?Set AWS_SECRET_ACCESS_KEY for the backup IAM user}"

cd "${HOME}/musicsamples"

backup_dir="${HOME}/db_backups"
mkdir -p "${backup_dir}"

backup_date="$(date +%Y-%m-%d)"
backup_filename="${backup_date}_musicsamples_db.sqlite3"
local_backup_path="${backup_dir}/${backup_filename}"

cp production.sqlite3 "${local_backup_path}"

# Ensure the temporary copy is always removed, even if the upload fails.
cleanup() {
  rm -f "${local_backup_path}"
}
trap cleanup EXIT

s3_prefix="${AWS_BACKUP_PREFIX:-}"
s3_prefix="${s3_prefix#/}"
s3_prefix="${s3_prefix%/}"
if [[ -n "${s3_prefix}" ]]; then
  s3_key="${s3_prefix}/${backup_filename}"
else
  s3_key="${backup_filename}"
fi

aws s3 cp "${local_backup_path}" "s3://${AWS_BACKUP_BUCKET}/${s3_key}"
