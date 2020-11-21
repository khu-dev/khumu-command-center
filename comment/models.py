from django.db import models
from article.models import Article
from user.models import KhumuUser
# Create your models here.
from khumu import settings

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now=True)
    kind = models.CharField(max_length=12, choices=[
        ("anonymous", "anonymous"),
        ("named", "named")],
        default="anonymous")
    state = models.CharField(max_length=12, choices=[
        ('exists', 'exists'),
        ("withdrawal", "withdrawal"),
        ("deleted", "deleted")],
        default="exists")


class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True)

