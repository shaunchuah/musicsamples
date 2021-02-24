from rest_framework import serializers
from .models import Sample

class SampleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            'musicsampleid', 
            'sample_location', 
            'sample_sublocation',
            ]
        lookup_field = 'musicsampleid'

class SampleIsFullyUsedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            'musicsampleid', 
            'is_fully_used', 
            ]
        lookup_field = 'musicsampleid'
        
