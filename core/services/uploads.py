# /Users/chershiongchuah/Developer/musicsamples/core/services/uploads.py
# This module contains the FileDirectUploadService for handling file uploads.
# It coordinates upload processes and integrates with storage backends.

import logging
from datetime import datetime, timedelta
from typing import Optional

from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from app.models import DataStore, StudyIdentifier, file_generate_name, file_upload_path


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
        sampling_date: Optional[datetime] = None,
        study_id: Optional[str] = None,
        uploaded_by=None,
    ) -> dict:
        if study_id:
            study_id = study_id.upper()
            study_identifier, _ = StudyIdentifier.objects.get_or_create(name=study_id)
            formatted_file_name = file_generate_name(file_name, study_name, study_id)
        else:
            formatted_file_name = file_generate_name(file_name, study_name)
            study_identifier = None

        file = DataStore(
            category=category,
            study_name=study_name,
            music_timepoint=music_timepoint,
            marvel_timepoint=marvel_timepoint,
            sampling_date=sampling_date,
            comments=comments,
            study_id=study_identifier,
            file_type=file_name.split(".")[-1],
            original_file_name=file_name,
            formatted_file_name=formatted_file_name,
            uploaded_by=uploaded_by,
            file=None,
        )
        file.full_clean()
        file.save()

        upload_path = file_upload_path(file, formatted_file_name)

        file.file = file.file.field.attr_class(file, file.file.field, upload_path)  # type: ignore
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
        return {"id": file.pk, "upload_url": upload_url}

    @transaction.atomic
    def finish(self, *, file: DataStore) -> DataStore:
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file
