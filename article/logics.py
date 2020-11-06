from django.db.models import QuerySet
from article.models import Article
from article.serializers import ArticleSerializer
from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework.request import Request
# from typing import Union, List
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer

def get_article_list(ctx, *args, **kwargs):
    result = []
    articles = Article.objects.filter(*args, **kwargs)
    s = ArticleSerializer(context=ctx, data=articles, many=True) # model serializer는 many가 True여야만하는듯하다.
    s.is_valid()  # is_valid create data
    articles_data = s.data
    for article, article_data in zip(articles, articles_data):
        article_data["author"] = get_article_author_simply(article)
        result.append(article_data)

    return result


def get_article_author_simply(article: Article) -> dict:
    author = KhumuUser.objects.filter(username__exact=article.author.username)
    s = KhumuUserSimpleSerializer(data=author, many=True)# 얘는 model serializer를 사용하지 않으므로 many=False 가능하긴함
    s.is_valid()
    author_data = {} if not s else s.data[0]
    if author_data:
        return {"type": "active", "username": author_data["username"]}
    else:
        return {"type": "withdrawl", "username": None}
