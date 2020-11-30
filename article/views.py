import json
import time

from article.models import Article, LikeArticle
from comment.serializers import CommentSerializer
from rest_framework import viewsets, pagination, permissions, views
from rest_framework import response
from rest_framework.parsers import JSONParser, MultiPartParser
from article.serializers import ArticleSerializer, LikeArticleSerializer
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse
from user.serializers import KhumuUserSimpleSerializer
from user.models import KhumuUser
from rest_framework.pagination import PageNumberPagination


class ArticlePagination(pagination.PageNumberPagination):

    page_size = 400  # 임의로 설정하느라 우선 크게 잡았음.

    def get_paginated_response(self, data):
        return response.Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })


class ArticleViewSet(viewsets.ModelViewSet):

    parser_classes = (JSONParser, MultiPartParser)

    def get_queryset(self):
        options = {}
        if self.request.query_params.get('board'):
            return Article.objects.filter(board_id=self.request.query_params['board']).order_by("-created_at")
        return Article.objects.all().order_by("-created_at")

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArticlePagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
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
        return DefaultResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data
        if not is_author_or_admin(request.user.get_username(), article.author.username):
            return UnAuthorizedResponse("You're not an admin neither an author.")

        return DefaultResponse(article_serialized)


class LikeArticleToggleView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, format=None):
        """
        좋아요를 토글한다.
        :param request:
        :param format:
        :return:
        """

        articleID = request.data['article']
        username = request.user.username
        likes = LikeArticle.objects.filter(user_id=username, article_id=articleID)

        if Article.objects.filter(id=articleID, author_id=username).exists():
            return DefaultResponse(False, message="It is not allowed to like comments of yourself", status=400)
        if len(likes) == 0:
            s = LikeArticleSerializer(data={"article": articleID, "user": username})
            is_valid = s.is_valid()
            if is_valid:
                s.save()
                return DefaultResponse(True, status=201)
            else:
                return DefaultResponse(False, message=str(s.errors), status=400)
        else:
            likes.delete()
            return response.Response(status=204)
