from django.db import models
from django.contrib.auth.models import User
from article.models import Article
# Create your models here.
from khumu import settings

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
