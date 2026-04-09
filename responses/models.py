from django.db import models
from django.conf import settings
from cases.models import Case

User = settings.AUTH_USER_MODEL


class Response(models.Model):

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    responder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name= 'case_responses'
    )

    is_auto = models.BooleanField(default=False)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_auto:
            return f"Auto Response for Case {self.case_id}"
        return f"Response by {self.responder} for Case {self.case_id}"



