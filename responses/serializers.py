from rest_framework import serializers
from .models import Response

class DoctorResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'case', 'message']
        read_only_fields = ['id']