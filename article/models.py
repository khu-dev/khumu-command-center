from django.db import models
# Create your models here.
from khumu import settings
from board.models import Board
from django.core.serializers.json import DjangoJSONEncoder
from user.models import KhumuUser
from cacheops import invalidate_obj

class Article(models.Model):
    class Meta:
        ordering = ("-created_at",)
    board = models.ForeignKey(Board, on_delete=models.SET_DEFAULT, default='temporary', null=False)
    title = models.CharField(max_length=300, null=False, blank=False)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_DEFAULT, default='deleted', null=True, blank=True)
    is_hot = models.BooleanField(default=False)
    content = models.TextField(null=True, blank=True)
    images = models.JSONField(null=False, blank=True, default=list)
    kind = models.CharField(max_length=16, default="anonymous", null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

class LikeArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        invalidate_obj(self.article)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        invalidate_obj(self.article)

class BookmarkArticle(models.Model):
    class Meta:
        ordering = ("-created_at",)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        invalidate_obj(self.article)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        invalidate_obj(self.article)

class StudyArticleStudyField(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=128, null=False, blank=False)

class StudyArticle(models.Model):
    class Meta:
        ordering = ("-created_at",)
    title = models.CharField(max_length=300, null=False, blank=False)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    numOfPeople = models.CharField(max_length=300, null=False, blank=False)
    term = models.CharField(max_length=128, null=False, blank=False)
    study_method = models.CharField(max_length=64)  # 비대면인지, 대면인지
    study_frequency = models.CharField(max_length=64)  # 스터디 주기는 어떻게 할 건지
    study_field = models.ForeignKey(StudyArticleStudyField, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    detailed_study_field = models.CharField(max_length=128, null=True, blank=True, default=None)
    content = models.TextField(null=True, blank=True)
    images = models.JSONField(null=False, blank=True, default=list)
    kind = models.CharField(max_length=16, default="anonymous", null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

class BookmarkStudyArticle(models.Model):
    class Meta:
        ordering = ("-created_at",)
    study_article = models.ForeignKey(StudyArticle, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
