#!/usr/bin/env python
import csv
import os

import django
from django.db import transaction

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

# Import your models after Django setup
from app.models import Sample  # noqa: E402


def update_timepoints_from_csv(csv_filepath):
    """
    Update music_timepoint values from a CSV file with columns sample_id and music_timepoint
    Runs all updates in a single transaction
    """
    updated_count = 0
    errors = []

    # Read all data from CSV first to validate before starting transaction
    updates = []
    with open(csv_filepath, "r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            sample_id = row.get("sample_id")
            music_timepoint = row.get("likely_timepoint")

            # Skip rows with missing data
            if not sample_id or not music_timepoint:
                errors.append(f"Missing data in row: {row}")
                continue

            updates.append((sample_id, music_timepoint))

    # Execute all updates in a single transaction
    try:
        with transaction.atomic():
            for sample_id, music_timepoint in updates:
                try:
                    # Find the sample by sample_id and update its timepoint
                    sample = Sample.objects.get(sample_id=sample_id)
                    sample.music_timepoint = music_timepoint
                    sample.save()
                    updated_count += 1
                except Sample.DoesNotExist:
                    errors.append(f"Sample not found: {sample_id}")
                    # Don't raise here to collect all errors
    except Exception as e:
        errors.append(f"Transaction failed: {str(e)}")
        return 0, errors  # No updates if transaction fails

    return updated_count, errors


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python update_timepoints.py <csv_filepath>")
        sys.exit(1)

    csv_filepath = sys.argv[1]

    # Confirm before running on production
    print(f"This will update music_timepoint values for samples in {csv_filepath}.")
    confirm = input("Are you sure you want to proceed? (y/n): ")

    if confirm.lower() != "y":
        print("Update canceled.")
        sys.exit(0)

    updated, errors = update_timepoints_from_csv(csv_filepath)

    print(f"Updated {updated} samples successfully")

    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
