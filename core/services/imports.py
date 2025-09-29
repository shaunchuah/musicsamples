# /Users/chershiongchuah/Developer/musicsamples/core/services/imports.py
# This module provides import services for study identifiers and clinical data.
# It processes data imports from dataframes and ensures data integrity.

import pandas as pd
from django.db import transaction

from app.models import ClinicalData, StudyIdentifier


class StudyIdentifierImportService:
    @staticmethod
    @transaction.atomic
    def import_from_dataframe(df):
        """
        Import study identifiers from a DataFrame
        Returns a dictionary with counts of processed records
        """
        # Initialize counters and collections
        updated = 0
        skipped = 0
        new_identifiers = []

        # Get existing identifiers to avoid duplicates
        existing_identifiers = {}

        # Build mapping of existing identifiers - both regular and suffixed
        for si in StudyIdentifier.objects.all():
            existing_identifiers[si.name] = si

            # For suffixed IDs, store the base name too for easy lookup
            if si.name.endswith("-P"):
                base_name = si.name[:-2]
                if base_name not in existing_identifiers:
                    existing_identifiers[base_name] = si
            elif si.name.endswith("-HC"):
                base_name = si.name[:-3]
                if base_name not in existing_identifiers:
                    existing_identifiers[base_name] = si

        # Process each row in the dataframe
        for _, row in df.iterrows():
            name = row.get("study_id", "").strip().upper()
            if not name:  # Skip empty identifiers
                continue

            # Check if this ID already exists (either direct match or as a suffixed version)
            if name in existing_identifiers:
                study_identifier = existing_identifiers[name]
                needs_update = False

                # Check if updates are needed and fields are present
                fields_to_check = [
                    "study_name",
                    "study_center",
                    "study_group",
                    "sex",
                    "age",
                    "genotype_data_available",
                    "nod2_mutation_present",
                    "il23r_mutation_present",
                ]
                for field in fields_to_check:
                    # Only consider fields that are present in the row
                    if field in row and pd.notna(row[field]):
                        # Convert types for proper comparison
                        current_value = getattr(study_identifier, field)
                        new_value = row[field]

                        # Handle age specifically since it's an integer field
                        if field == "age":
                            if pd.isna(new_value):
                                new_value = None
                            elif new_value is not None:
                                new_value = int(new_value)

                        # For boolean fields like genotype_data_available
                        if field in ["genotype_data_available", "nod2_mutation_present", "il23r_mutation_present"]:
                            if pd.isna(new_value):
                                new_value = False
                            else:
                                new_value = bool(new_value)

                        # Compare and update if different
                        if current_value != new_value:
                            setattr(study_identifier, field, new_value)
                            needs_update = True

                if needs_update:
                    study_identifier.save()
                    updated += 1
                else:
                    skipped += 1
                continue

            # If we reach here, this is a completely new identifier
            study_identifier = StudyIdentifier(
                name=name,
                study_name=row.get("study_name"),
                study_center=row.get("study_center"),
                study_group=row.get("study_group"),
                sex=row.get("sex"),
                age=row.get("age") if "age" in row and pd.notna(row["age"]) else None,
                genotype_data_available=row.get("genotype_data_available", False),
                nod2_mutation_present=row.get("nod2_mutation_present", False),
                il23r_mutation_present=row.get("il23r_mutation_present", False),
            )
            new_identifiers.append(study_identifier)

        # Bulk create new objects
        created = 0
        if new_identifiers:
            StudyIdentifier.objects.bulk_create(new_identifiers)
            created = len(new_identifiers)

        return {"total": len(df), "created": created, "updated": updated, "skipped": skipped}


class ClinicalDataImportService:
    @staticmethod
    @transaction.atomic
    def import_from_dataframe(df):
        """
        Import clinical data from DataFrame with different merging strategies by study
        Returns a dictionary with counts of processed records
        """
        # Initialize counters
        created = 0
        updated = 0
        skipped = 0
        errors = []

        # Process each row
        for index, row in df.iterrows():
            try:
                # Find the study identifier
                study_id_name = row.get("study_id")
                if not study_id_name:
                    skipped += 1
                    continue

                study_id = StudyIdentifier.objects.filter(name=study_id_name).first()
                if not study_id:
                    skipped += 1
                    continue

                # Determine study type to use appropriate matching strategy
                study_name = study_id.study_name.lower() if study_id.study_name else ""

                if "gidamps" in study_name:
                    # For GI-DAMPs: Use study_id and sample_date
                    sample_date = (
                        pd.to_datetime(row.get("sample_date")).date() if pd.notna(row.get("sample_date")) else None
                    )
                    if not sample_date:
                        skipped += 1
                        continue

                    # Get or create clinical data entry for GI-DAMPs
                    clinical_data, created_new = ClinicalData.objects.get_or_create(
                        study_id=study_id,
                        sample_date=sample_date,
                    )

                elif "music" in study_name:
                    # For MUSIC and Mini-MUSIC: Use study_id and music_timepoint
                    music_timepoint = row.get("music_timepoint")
                    if not music_timepoint:
                        skipped += 1
                        continue

                    # Get sample_date if available (optional for MUSIC/Mini-MUSIC)
                    sample_date = (
                        pd.to_datetime(row.get("sample_date")).date() if pd.notna(row.get("sample_date")) else None
                    )

                    # Get or create clinical data entry for MUSIC/Mini-MUSIC
                    clinical_data, created_new = ClinicalData.objects.get_or_create(
                        study_id=study_id,
                        music_timepoint=music_timepoint,
                    )

                    # Update sample_date if provided
                    if sample_date:
                        clinical_data.sample_date = sample_date
                else:
                    # Default fallback to sample_date for unknown studies
                    sample_date = (
                        pd.to_datetime(row.get("sample_date")).date() if pd.notna(row.get("sample_date")) else None
                    )
                    if not sample_date:
                        skipped += 1
                        continue

                    clinical_data, created_new = ClinicalData.objects.get_or_create(
                        study_id=study_id,
                        sample_date=sample_date,
                    )

                # Update fields - common for all study types
                # Use a list to track which fields were updated
                updated_fields = []

                # For each field, set to value or None if NA, and always update if different
                clinical_fields = [
                    "crp",
                    "calprotectin",
                    "endoscopic_mucosal_healing_at_3_6_months",
                    "endoscopic_mucosal_healing_at_12_months",
                    # Add more clinical fields as needed
                ]
                for field in clinical_fields:
                    if field in row:
                        value = row[field]
                        if pd.isna(value):
                            value = None
                        if getattr(clinical_data, field) != value:
                            setattr(clinical_data, field, value)
                            updated_fields.append(field)

                # Only save if there are actual updates or it's a new record
                if updated_fields or created_new:
                    clinical_data.save()

                    if created_new:
                        created += 1
                    else:
                        updated += 1
                else:
                    skipped += 1

            except Exception as e:
                # Log the error but continue processing other rows
                import logging

                logging.exception(f"Error processing row {index}: {e}")
                errors.append(f"Row {index}: {str(e)}")
                skipped += 1

        return {"created": created, "updated": updated, "skipped": skipped, "errors": errors if errors else None}
