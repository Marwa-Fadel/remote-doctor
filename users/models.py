from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('civilian', 'Civilian'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.username




class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    SPECIALTIES = [
        ('general', 'General'),
        ('burn', 'Burn'),
        ('trauma', 'Trauma'),
        ('surgery', 'Surgery'),
    ]

    specialty = models.CharField(max_length=50, choices=SPECIALTIES)

    def __str__(self):
        return str(self.user)