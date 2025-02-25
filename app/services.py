import logging
from datetime import datetime, timedelta

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
        study_id: str = None,
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
            comments=comments,
            study_id=study_identifier if study_id else None,
            file_type=file_name.split(".")[-1],
            original_file_name=file_name,
            formatted_file_name=formatted_file_name,
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
