import json
import time

from article.models import Article, LikeArticle, BookmarkArticle
from board.models import Board
from comment.serializers import CommentSerializer
from rest_framework import viewsets, pagination, permissions, views
from rest_framework import response
from rest_framework.parsers import JSONParser, MultiPartParser
from article.serializers import ArticleSerializer, LikeArticleSerializer, BookmarkArticleSerializer
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

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArticlePagination

    def get_queryset(self):
        options = {}
        board_name = self.request.query_params.get('board')
        if board_name == 'recent':
            return self._get_recent_articles()
        elif board_name == 'my':
            return self._get_my_articles()
        elif board_name == 'liked':
            return self._get_liked_articles()
        elif board_name == 'bookmarked':
            return self._get_bookmarked_articles()
        elif board_name == 'commented':
            return self._get_commented_articles()
        elif board_name:
            return Article.objects.filter(board_id=self.request.query_params['board'])

        # board_name이 정의되지 않은 경우는 그냥 all
        return Article.objects.all()

    # 추후 기능: 사용자별 feed를 제공해야함.
    def _get_recent_articles(self):
        return Article.objects.all()

    def _get_my_articles(self):
        return self.request.user.article_set.all()

    def _get_bookmarked_articles(self):
        articles = []
        for bookmarkArticle in self.request.user.bookmarkarticle_set.all():
            articles.append(bookmarkArticle.article)
        return articles

    def _get_liked_articles(self):
        articles = []
        for likeArticle in self.request.user.likearticle_set.all():
            articles.append(likeArticle.article)
        return articles

    def _get_commented_articles(self):
        articles = []
        for comment in self.request.user.comment_set.all().order_by('-created_at'):
            if comment.article not in articles:
                articles.append(comment.article)
        return articles

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return DefaultResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data

        return DefaultResponse(article_serialized)


class LikeArticleToggleView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id: str, format=None):
        """
        좋아요를 토글한다.
        :param request:
        :param format:
        :return:
        """
        username = request.user.username
        likes = LikeArticle.objects.filter(user_id=username, article_id=id)

        if Article.objects.filter(id=id, author_id=username).exists():
            return DefaultResponse(False, message="자신의 게시물은 좋아요할 수 없습니다.", status=400)
        if len(likes) == 0:
            s = LikeArticleSerializer(data={"article": id, "user": username})
            is_valid = s.is_valid()
            if is_valid:
                s.save()
                return DefaultResponse(True, status=201)
            else:
                return DefaultResponse(False, message=str(s.errors), status=400)
        else:
            likes.delete()
            return response.Response(status=204)


class BookmarkArticleToggleView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id: str, format=None):
        """
        좋아요를 토글한다.
        :param request:
        :param format:
        :return:
        """

        article_id = request.data['article']
        username = request.user.username
        bookmarks = BookmarkArticle.objects.filter(user_id=username, article_id=id)

        if Article.objects.filter(id=id, author_id=username).exists():
            return DefaultResponse(False, message="자신의 게시물은 북마크할 수 없습니다.", status=400)
        if len(bookmarks) == 0:
            s = BookmarkArticleSerializer(data={"article": id, "user": username})
            is_valid = s.is_valid()
            if is_valid:
                s.save()
                return DefaultResponse(True, status=201)
            else:
                return DefaultResponse(False, message=str(s.errors), status=400)
        else:
            bookmarks.delete()
            return response.Response(status=204)
