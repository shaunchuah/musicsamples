from rest_framework import serializers

from datasets.models import Dataset, DatasetAnalytics, DataSourceStatusCheck


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["study_name", "name", "description", "json"]


class DataSourceStatusCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceStatusCheck
        fields = ["data_source", "response_status", "error_message"]


class DatasetAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetAnalytics
        fields = ["name", "data"]
