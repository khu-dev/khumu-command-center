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

class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def get_queryset(self):
        print("ArticleViewSet get_queryset")
        return Article.objects.all()

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        articles = serializer.data

        for article in articles:
            author_username = article["author"]
            author = KhumuUser.objects.filter(username=author_username)[0]
            author_serialized = KhumuUserSimpleSerializer(author)
            article["author"] = author_serialized.data
        # result = get_article_list(self.get_serializer_context(), *args, **query_options)
        return response.Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data
        if not is_author_or_admin(request.user.get_username(), article.author.username):
            return UnAuthorizedResponse("You're not an admin neither an author.")

        return response.Response(article_serialized)
