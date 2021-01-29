from django.db import models
# Create your models here.
from khumu import settings
from board.models import Board
from django.core.serializers.json import DjangoJSONEncoder
from user.models import KhumuUser


class ArticleTag(models.Model):
    name = models.CharField(primary_key=True, unique=True, max_length=32, null=False, blank=False)

class Article(models.Model):
    class Meta:
        ordering = ("-created_at",)
    board = models.ForeignKey(Board, on_delete=models.SET_DEFAULT, default='temporary', null=False)
    title = models.CharField(max_length=300, null=False, blank=False)
    tags = models.ManyToManyField(ArticleTag)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    images = models.JSONField(null=False, blank=True, default=list)
    kind = models.CharField(max_length=16, default="anonymous", null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)


class LikeArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=True, blank=True)


class BookmarkArticle(models.Model):
    class Meta:
        ordering = ("-created_at",)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)


class FollowArticleTag(models.Model):
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False, blank=False)
    tag = models.ForeignKey(ArticleTag, on_delete=models.CASCADE, null=False, blank=False)
    followed_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)