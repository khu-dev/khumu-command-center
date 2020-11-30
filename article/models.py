from django.db import models
# Create your models here.
from khumu import settings
from board.models import Board
from jsonfield import JSONField
from user.models import KhumuUser


class Article(models.Model):
    class Meta:
        ordering = ("-created_at",)
    board = models.ForeignKey(Board, on_delete=models.SET_DEFAULT, default='default', null=False)
    title = models.CharField(max_length=300, null=False, blank=False)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    images = JSONField(null=True, blank=True)
    kind = models.CharField(max_length=16, default="anonymous", null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)


class LikeArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=True, blank=True)
