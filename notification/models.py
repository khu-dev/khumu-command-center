from django.db import models

from article.models import Article
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

class ArticleNotificationSubscription(models.Model):
    '''
    게시판에 대한 알림 사항들을 구독하기
    알림 수신 대상자: 해당 게시판에 대한 알림 구독이 존재하며 is_activated = True인 유저
    대상이 아닌 자: 해당 게시판에 대한 알림 구독이 존재하지 않거나 존재함에도 불구하고 is_activate = False인 유저
    '''
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False, blank=False)
    subscriber = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False, blank=False)
    is_activated = models.BooleanField(null=False, blank=False)

class PushSubscription(models.Model):
    device_token = models.CharField(max_length=320, primary_key=True, null=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)