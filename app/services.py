import logging
from datetime import datetime, timedelta

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from django.conf import settings


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
