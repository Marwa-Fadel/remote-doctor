from rest_framework import serializers
from .models import EmergencyGuide

class EmergencyGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyGuide
        fields = ['case_type', 'title', 'instructions']
