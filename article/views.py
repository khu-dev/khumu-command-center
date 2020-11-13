import json
import time

from article.models import Article
from comment.serializers import CommentSerializer
from rest_framework import viewsets, pagination
from rest_framework import permissions
from rest_framework import response
from article.serializers import ArticleSerializer
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse
from user.serializers import KhumuUserSimpleSerializer
from user.models import KhumuUser
from rest_framework.pagination import PageNumberPagination


class ArticlePagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return response.Response({
            'status_code': 200,
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def get_queryset(self):
        if self.request.query_params.get('board'):
            return Article.objects.filter(board_id=self.request.query_params['board'])
        return Article.objects.all()

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArticlePagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
        print(page)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # for article in articles:
        #     author_username = article["author"]
        #     author = KhumuUser.objects.filter(username=author_username)[0]
        #     author_serialized = KhumuUserSimpleSerializer(author)
        #     article["author"] = author_serialized.data
        # result = get_article_list(self.get_serializer_context(), *args, **query_options)
        return DefaultResponse(200, serializer.data)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data
        if not is_author_or_admin(request.user.get_username(), article.author.username):
            return UnAuthorizedResponse("You're not an admin neither an author.")

        return DefaultResponse(200, article_serialized)

