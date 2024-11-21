from rest_framework import serializers

from datasets.models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["study_name", "name", "description", "json"]
