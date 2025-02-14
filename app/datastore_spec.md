# DataStore Specification

## Overview

This document outlines the data structure for a File object that facilitates systematic data organization. The File object comprises:

- **Study Name**
- **Study ID**
- **Timepoint** (if applicable)

## File Naming Convention

Files must be named using the following format:

```sh
StudyName_StudyID_Timepoint_OriginalFileName_UUIDhex.ext
```

## Container Organization

Files should be stored in categorized containers as shown below:

```sh
FileCategory/filename
```

## Azure Storage Containers

Utilize the following Azure containers for file storage:

- **Development:** gtrac-store-dev
- **Production:** gtrac-store

## Connection Method

Files are accessed via a connection string.

## Frontend File Upload Process

1. Files are directly uploaded from the client to Azure Blob Storage.
2. A corresponding File object is created in Django.
3. A URL is generated for uploading to Azure, ensuring the filename matches the Django record.
4. The file is uploaded to Azure Blob Storage.
5. Upon completion, Django is notified to confirm successful upload.

## Important Notes

- Once a file is uploaded, it cannot be edited.
