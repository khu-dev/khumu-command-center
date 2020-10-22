from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from khumu import settings
from board.models import Board
from jsonfield import JSONField


class Article(models.Model):
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField(null=True)
    images = JSONField(null=True)
    create_at = models.DateTimeField(auto_now_add=True)
