from django.db import models

class EmergencyGuide(models.Model):

    CASE_TYPE_CHOICES = (
        ('bleeding', 'Bleeding'),
        ('burn', 'Burn'),
        ('fracture', 'Fracture'),
        ('other', 'Other'),
    )

    case_type = models.CharField(
        max_length=20,
        choices=CASE_TYPE_CHOICES,
        unique=True  
    )

    title = models.CharField(max_length=255)
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.get_case_type_display()} - {self.title}"
