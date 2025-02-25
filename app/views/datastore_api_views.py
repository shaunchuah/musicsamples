from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import DataStore
from app.services import FileDirectUploadService


class FileDirectUploadStartApi(APIView):
    class InputSerializer(serializers.Serializer):
        category = serializers.CharField()
        study_name = serializers.CharField()
        music_timepoint = serializers.CharField(required=False, allow_blank=True)
        marvel_timepoint = serializers.CharField(required=False, allow_blank=True)
        study_id = serializers.CharField(required=False, allow_blank=True)
        comments = serializers.CharField(required=False, allow_blank=True)

        file_name = serializers.CharField()

        def validate_study_id(self, value):
            if value == "":
                return None
            return value

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        presigned_data = FileDirectUploadService.start(self, **serializer.validated_data)

        return Response(data=presigned_data)


class FileDirectUploadFinishApi(APIView):
    class InputSerializer(serializers.Serializer):
        file_id = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]

        file = get_object_or_404(DataStore, id=file_id)
        FileDirectUploadService.finish(self, file=file)

        return Response({"id": file.id})
