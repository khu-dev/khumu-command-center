from django.db import models
from user.models import KhumuUser
# Create your models here.
from khumu import settings


class Board(models.Model):
    name = models.CharField(max_length=15, null=False, primary_key=True) # this is in english
    display_name = models.CharField(max_length=16, null=False)
    description = models.CharField(max_length=150, null=True, blank=True)
    admin = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
