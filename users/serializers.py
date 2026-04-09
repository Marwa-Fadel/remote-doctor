from rest_framework import serializers
from django.db import transaction
from .models import User, DoctorProfile

class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    مُحوِّل لعرض وتعديل الملف الشخصي للطبيب.
    """
    class Meta:
        model = DoctorProfile
        fields = ['specialty']


class UserSerializer(serializers.ModelSerializer):
    """
    مُحوِّل عام لعرض بيانات المستخدم.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'phone_number']


class DoctorDetailSerializer(serializers.ModelSerializer):
    """
    مُحوِّل لعرض الملف الشخصي الكامل للطبيب (بيانات المستخدم + بيانات الطبيب).
    """
    profile = DoctorProfileSerializer(source='doctorprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'is_available', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    """
    المُحوِّل الأساسي لإنشاء حساب جديد (للمرضى والأطباء).
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    specialty = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'specialty']

    def validate_role(self, value):
        if value not in ['civilian', 'doctor']:
            raise serializers.ValidationError("Role must be either 'civilian' or 'doctor'.")
        return value

    def create(self, validated_data):
        role = validated_data.get('role')
        specialty = validated_data.pop('specialty', None)

        if role == 'doctor' and not specialty:
            raise serializers.ValidationError({'specialty': 'This field is required for doctors.'})

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=validated_data['username'],
                    password=validated_data['password'],
                    email=validated_data.get('email', ''),
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                    phone_number=validated_data.get('phone_number', ''),
                    role=role
                )

                if role == 'doctor':
                    DoctorProfile.objects.create(user=user, specialty=specialty)
            
            return user

        except Exception as e:
            raise serializers.ValidationError(f"An error occurred: {str(e)}")





class EmergencyLoginSerializer(serializers.Serializer):
    """
    مُحوِّل بسيط لاستقبال رقم الهاتف في بوابة الطوارئ.
    """
    phone_number = serializers.CharField(required=True, allow_blank=False)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value
