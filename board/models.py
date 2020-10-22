from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from khumu import settings


class Board(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=150)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
