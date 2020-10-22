from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class KhumuUser(User):
    type = models.CharField(max_length=16, default="khumu")
    nickname = models.CharField(max_length=10, default="흡혈형사")
    student_number = models.CharField(max_length=10, default="2000123123")
    memo = models.TextField(max_length=150, default="안녕, 잘 부탁해")


