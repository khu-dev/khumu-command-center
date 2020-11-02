from django.db import models
from article.models import Article
from user.models import KhumuUser
# Create your models here.
from khumu import settings

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(max_length=12, choices=[
        ("anonymous", "anonymous"),
        ("named", "named"),
        ("withdrawal", "withdrawal"),
        ("deleted", "deleted")],
        default="anonymous")

class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)

