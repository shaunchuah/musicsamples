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
        
