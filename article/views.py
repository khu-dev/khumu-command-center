import json
import time

from article.models import Article
from comment.serializers import CommentSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import response
from article.serializers import ArticleSerializer
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse
from user.serializers import KhumuUserSimpleSerializer
from user.models import KhumuUser
from article.logics import get_comments

class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def get_queryset(self):
        print("ArticleViewSet get_queryset")
        queryset = Article.objects.all()

        board_pk = self.request.query_params.get('board')
        if board_pk:
            queryset = queryset.filter(board__pk=board_pk)

        author_name = self.request.query_params.get('author')
        if author_name:
            queryset = queryset.filter(author__username=author_name)

        return queryset

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        articles = self.get_queryset()
        articles_serialized = ArticleSerializer(context=self.get_serializer_context(), data=articles, many=True)
        articles_serialized.is_valid()
        articles_serialized = articles_serialized.data

        for article_serialized in articles_serialized:
            author_username = article_serialized["author"]
            author = KhumuUser.objects.filter(username__exact=author_username)
            author_serialized = KhumuUserSimpleSerializer(data=author, many=True)
            author_serialized.is_valid()
            author_serialized = author_serialized.data
            if author_serialized:
                article_serialized["author"] = author_serialized
            else:
                article_serialized["author"] = {"username":None} # This will be converted into null
        return response.Response(articles_serialized)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data
        if not is_author_or_admin(request.user.get_username(), article.author.username):
            return UnAuthorizedResponse("You're not an admin neither an author.")

        article_serialized['comments'] = get_comments(article, self.get_serializer_context())

        return response.Response(article_serialized)
