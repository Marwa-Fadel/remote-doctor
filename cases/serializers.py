from rest_framework import serializers
from .models import Case
from responses.models import Response as CaseResponse

# 💡 إصلاح خطأ 4: إزالة المُحوِّل المكرر ودمج الحقول في واحد

class CaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id',
            'description',
            'case_type',
            'location_text',
            'location_lat',
            'location_lng',
            # لا نضع 'priority' هنا لأنها ستحسب تلقائياً في الواجهة
        ]
        read_only_fields = ['id']


class ResponseSerializer(serializers.ModelSerializer):
    # هذا المُحوِّل لعرض الردود داخل تفاصيل الحالة
    responder_username = serializers.CharField(source='responder.username', read_only=True)
    class Meta:
        model = CaseResponse
        fields = ['id', 'responder_username', 'is_auto', 'message', 'created_at']


class CaseListSerializer(serializers.ModelSerializer):
    responses = ResponseSerializer(many=True, read_only=True)
    priority = serializers.CharField(source='get_priority_display', read_only=True) 
    
    class Meta:
        model = Case
        fields = [
            'id',
            'description',
            'case_type',
            'priority', 
            'status',
            'location_text',
            'location_lat',
            'location_lng',
            'created_at',
            'responses'
        ]
