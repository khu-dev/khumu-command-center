from django.db import models
from user.models import KhumuUser
# Create your models here.
from khumu import settings

class Notification(models.Model):
    kind = models.CharField(max_length=16, null=False, blank=False, default="mock")
    title = models.TextField(null=False, blank=False)
    content = models.TextField(null=False, blank=False)
    is_read = models.BooleanField(null=False, blank=False)
    recipient = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)