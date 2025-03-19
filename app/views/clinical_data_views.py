import json
import logging

import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app.services import ClinicalDataImportService

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def import_clinical_data(request):
    """
    API endpoint to import clinical data from CSV or JSON.
    """
    try:
        # Handle CSV file upload
        if "csv_file" in request.FILES:
            df = pd.read_csv(request.FILES["csv_file"])
        # Handle JSON data
        elif "json_data" in request.data:
            json_data = request.data["json_data"]

            # Handle different JSON formats
            if isinstance(json_data, str):
                # Parse the JSON string
                try:
                    json_data = json.loads(json_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON format: {str(e)}")
                    return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure the JSON is in a list format for DataFrame
            if isinstance(json_data, dict):
                # If it's a single record as dictionary
                df = pd.DataFrame([json_data])
            elif isinstance(json_data, list):
                # If it's a list of records
                df = pd.DataFrame(json_data)
            else:
                logger.error(f"Invalid JSON data type: {type(json_data)}")
                return Response(
                    {"error": "JSON data must be a dictionary or a list of dictionaries"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "No data provided. Send either json_data or csv_file."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if DataFrame is empty
        if df.empty:
            return Response(
                {"error": "No data found in the provided file or JSON"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check required columns
        required_columns = ["study_id"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process data
        result = ClinicalDataImportService.import_from_dataframe(df)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        # Log error with more details
        logger.exception(f"Error processing clinical data import: {str(e)}")
        # Return error response
        return Response({"error": f"Error processing data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
