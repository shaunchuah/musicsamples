import logging
from datetime import datetime, timedelta

import pandas as pd
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from app.models import DataStore, StudyIdentifier, file_generate_name, file_upload_path


def azure_get_blob_service_client():
    return BlobServiceClient(
        account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=settings.AZURE_ACCOUNT_KEY,
    )


def azure_generate_download_link(file, download=False):
    """
    Pass in the file object stored on Azure Blob Storage.
    The blob path is constructed as <study_name>/<category>/<filename>.
    Generates a SAS token valid for 1 hour with read permission and,
    if download is True, an attachment disposition.
    """
    container_name = settings.AZURE_CONTAINER_NAME
    blob_name = f"{file.file.name}"

    expiration_time = datetime.utcnow() + timedelta(hours=1)

    try:
        sas_kwargs = {
            "account_name": settings.AZURE_ACCOUNT_NAME,
            "container_name": container_name,
            "blob_name": blob_name,
            "account_key": settings.AZURE_ACCOUNT_KEY,
            "permission": BlobSasPermissions(read=True),
            "expiry": expiration_time,
        }
        if download:
            sas_kwargs["content_disposition"] = "attachment"

        sas_token = generate_blob_sas(**sas_kwargs)
    except Exception as e:
        logging.error(e)
        return None

    download_url = (
        f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    )
    return download_url


def azure_delete_file(file):
    """
    Pass in the file
    """
    blob_service_client = azure_get_blob_service_client()
    container_name = settings.AZURE_CONTAINER_NAME
    blob_name = f"{file.file.name}"

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()
    except Exception as e:
        logging.error(e)
        return None
    return True


class FileDirectUploadService:
    @transaction.atomic
    def start(
        self,
        category: str,
        study_name: str,
        file_name: str,
        music_timepoint: str,
        marvel_timepoint: str,
        comments: str,
        sampling_date: datetime = None,
        study_id: str = None,
        uploaded_by=None,
    ) -> dict:
        if study_id:
            study_id = study_id.upper()
            study_identifier, _ = StudyIdentifier.objects.get_or_create(name=study_id)
            formatted_file_name = file_generate_name(file_name, study_name, study_id)
        else:
            formatted_file_name = file_generate_name(file_name, study_name)

        file = DataStore(
            category=category,
            study_name=study_name,
            music_timepoint=music_timepoint,
            marvel_timepoint=marvel_timepoint,
            sampling_date=sampling_date,
            comments=comments,
            study_id=study_identifier if study_id else None,
            file_type=file_name.split(".")[-1],
            original_file_name=file_name,
            formatted_file_name=formatted_file_name,
            uploaded_by=uploaded_by,
            file=None,
        )
        file.full_clean()
        file.save()

        upload_path = file_upload_path(file, formatted_file_name)

        file.file = file.file.field.attr_class(file, file.file.field, upload_path)
        file.save()

        try:
            sas_kwargs = {
                "account_name": settings.AZURE_ACCOUNT_NAME,
                "container_name": settings.AZURE_CONTAINER_NAME,
                "blob_name": upload_path,
                "account_key": settings.AZURE_ACCOUNT_KEY,
                "permission": BlobSasPermissions(write=True),
                "expiry": timezone.now() + timedelta(hours=1),
            }

            sas_token = generate_blob_sas(**sas_kwargs)
            upload_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{upload_path}?{sas_token}"

        except Exception as e:
            logging.error(e)
            return {"error": "Failed to generate upload URL"}
        return {"id": file.id, "upload_url": upload_url}

    @transaction.atomic
    def finish(self, *, file: DataStore) -> DataStore:
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file


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
