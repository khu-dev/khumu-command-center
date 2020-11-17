from django.db import models
# Create your models here.
from khumu import settings
from board.models import Board
from jsonfield import JSONField
from user.models import KhumuUser

class Article(models.Model):
    board = models.ForeignKey(Board, on_delete=models.SET_DEFAULT, default='default', null=False)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField(null=True, blank=True)
    images = JSONField(null=True)
    kind = models.CharField(max_length=16, default="anonymous")
    created_at = models.DateTimeField(auto_now_add=True)

class LikeArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False)
