from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Case(models.Model):

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    )

    PRIORITY_CHOICES = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    )

    CASE_TYPE_CHOICES = (
        ('bleeding', 'Bleeding'),
        ('burn', 'Burn'),
        ('fracture', 'Fracture'),
        ('other', 'Other'),
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cases'
    )
    description = models.TextField()
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, default='other')

    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    location_text = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    
    assigned_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_cases"
    )
    offline_id = models.UUIDField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"Case {self.id} - {self.case_type} - {self.get_priority_display()}"


class CaseImage(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='cases/')
    compressed_image = models.ImageField(
        upload_to='cases/compressed/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Case {self.case.id}"
