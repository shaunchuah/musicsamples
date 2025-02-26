import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app.services import StudyIdentifierImportService


@api_view(["POST"])
@permission_classes([IsAdminUser])  # Restrict to admins
def import_study_identifiers(request):
    """
    API endpoint to import study identifiers from JSON or CSV data.
    Needs json_data in request.data or csv_file in request.FILES.

    The Data needs the following 6 columns:
    - study_id
    - study_name
    - study_center
    - study_group
    - age
    - sex
    """
    try:
        # If sending JSON data
        if "json_data" in request.data:
            json_data = request.data["json_data"]
            # Handle case where json_data might be a string
            if isinstance(json_data, str):
                import json

                try:
                    json_data = json.loads(json_data)
                except json.JSONDecodeError as e:
                    return Response({"error": f"Invalid JSON format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure json_data is a list of dictionaries
            if not isinstance(json_data, list):
                return Response({"error": "JSON data must be an array of objects"}, status=status.HTTP_400_BAD_REQUEST)

            df = pd.DataFrame(json_data)
        # If sending a CSV file
        elif "csv_file" in request.FILES:
            df = pd.read_csv(request.FILES["csv_file"])
        else:
            return Response(
                {"error": "No data provided. Send either json_data or csv_file."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the data has required columns
        required_columns = ["study_id", "study_name", "study_center", "study_group", "age", "sex"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process the data
        result = StudyIdentifierImportService.import_from_dataframe(df)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Error processing data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
