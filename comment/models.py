from django.db import models
from article.models import Article, StudyArticle
from user.models import KhumuUser
# Create your models here.
from khumu import settings

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    study_article = models.ForeignKey(StudyArticle, on_delete=models.CASCADE, null=True)
    # deleted는 삭제된 유저를 칭하는 dummy user
    author = models.ForeignKey(KhumuUser, on_delete=models.SET_DEFAULT, default='deleted', null=True)
    content = models.TextField(max_length=500, null=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now=True, null=False)
    kind = models.CharField(max_length=12, choices=[
        ("anonymous", "anonymous"),
        ("named", "named")],
        default="anonymous", null=False)
    state = models.CharField(max_length=12, choices=[
        ('exists', 'exists'),
        ("withdrawal", "withdrawal"),
        ("deleted", "deleted")],
        default="exists", null=False)

class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(KhumuUser, on_delete=models.SET_DEFAULT, default='deleted', null=True)

