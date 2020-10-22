from django.db import models
from user.models import KhumuUser
# Create your models here.
from khumu import settings


class Board(models.Model):
    short_name = models.CharField(max_length=8)
    long_name = models.CharField(max_length=16)
    name = models.CharField(max_length=15) # this is in english
    description = models.CharField(max_length=150)
    admin = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)
