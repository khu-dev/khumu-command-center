from django.db.models import QuerySet
from article.models import Article
from article.serializers import ArticleSerializer
from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework.request import Request
# from typing import Union, List
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer


def get_article_comments(article:QuerySet, context):
    result = []
    article_author_username = article.author.username
    parent_comments = article.comment_set.filter(author__username=article_author_username, parent__isnull=True)
    for p in parent_comments.iterator():
        parent_obj = CommentSerializer(p, context)
        parent_obj.is_valid()
        parent_obj = parent_obj.data
        print("parent_obj")
        print(parent_obj)
        children_comments = Comment.objects.filter(parent__pk__exact=p.pk)
        # children_comments = Comment.objects.filter()
        for c in children_comments.iterator():
            cc = CommentSerializer(data=c, context=context)
            cc.is_valid()
            data = cc.data
            print(data)
        children_obj = CommentSerializer(data=children_comments, context=context, many=True)
        children_obj.is_valid()
        parent_obj["children"] = children_obj = children_obj.data
        result.append(parent_obj)
    return result


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
