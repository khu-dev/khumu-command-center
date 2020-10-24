from django.db.models import QuerySet
from article.models import Article
from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework.request import Request
# from typing import Union, List


def get_comments(article:QuerySet, context):
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