import datetime
import traceback
import urllib.parse as urlparse
from urllib.parse import parse_qs
from django.db.models import Count
import json
import time
from django.core.cache import cache
from rest_framework import viewsets, pagination, permissions, views, status, generics
from rest_framework import response
from rest_framework.parsers import JSONParser, MultiPartParser

from article.services import LikeArticleService, LikeArticleException
from khumu import settings, config
import message.publisher
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q
from article.models import *
from board.models import *

from article.serializers import *
from user.serializers import KhumuUserSimpleSerializer

logger = logging.getLogger(__name__)
class ArticlePagination(pagination.CursorPagination):

    page_size = 30  # 임의로 설정하느라 우선 크게 잡았음.
    ordering = '-created_at'
    def get_paginated_response(self, data):
        next_cursor = None
        # next_link = self.get_next_link()
        # 캐시 테스트 하느라 임시로 None
        next_link = None
        if next_link != None:
            parsed = urlparse.urlparse(next_link)
            next_cursor = parse_qs(parsed.query).get('cursor', None)

        return response.Response({
            'links': {
                'next': self.get_next_link(),
                'next_cursor': next_cursor,
                'previous': self.get_previous_link()
            },
            'count': len(self.page),
            'data': data
        })


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArticlePagination

    def get_queryset(self):
        board_name = self.request.query_params.get('board')
        q = self.request.query_params.get('q', '')
        queryset = None
        if board_name == 'following':
            queryset = self._get_articles_from_following()
        elif board_name == 'my':
            queryset = self._get_my_articles()
        elif board_name == 'liked':
            queryset = self._get_liked_articles()
        elif board_name == 'bookmarked':
            queryset = self._get_bookmarked_articles()
        elif board_name == 'commented':
            queryset = self._get_commented_articles()
        elif board_name == 'hot':
            queryset = Article.objects.filter(is_hot=True)
        elif board_name:
            queryset = Article.objects.filter(~Q(board__category__exact='temporary')).filter(board_id=self.request.query_params['board'])
        # 기본 쿼리셋
        else:
            queryset = Article.objects
        if len(q) != 0:
            queryset = queryset.filter(Q(title__contains=q) | Q(content__contains=q))
        # board_name이 정의되지 않은 경우는 임시 카테고리의 게시판 빼고 query
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        else: return ArticleSerializer

    # 사용자별 feed를 위한 최신 게시물을 제공해야함.
    def _get_articles_from_following(self):
        # following_board_names = FollowBoard.objects.filter(user_id=self.request.user.username).all().values('board__name')
        return Article.objects.filter(board__followboard__user__exact=self.request.user)
    # i, love, you
    # Following: you

    def _get_my_articles(self):
        return self.request.user.article_set.filter(~Q(board__category__exact='temporary'))


    def _get_bookmarked_articles(self):
        articles = []
        # Article.objects.filter(bookmarkarticle__user__username__exact=self.request.user.username)
        for bookmarkArticle in self.request.user.bookmarkarticle_set.all():
            if bookmarkArticle.article.board.category != 'temporary':
                articles.append(bookmarkArticle.article)
        return articles

    def _get_liked_articles(self):
        articles = []
        for likeArticle in self.request.user.likearticle_set.all():
            if likeArticle.article.board.category != 'temporary':
                articles.append(likeArticle.article)
        return articles

    def _get_commented_articles(self):
        articles = []
        for comment in self.request.user.comment_set.all().order_by('-created_at'):
            if comment.article.board.category != 'temporary' and comment.article not in articles:
                articles.append(comment.article)
        return articles

    def perform_create(self, serializer: ArticleSerializer):
        super().perform_create(serializer)
        if settings.SNS['enabled']:
            message.publisher.publish("article", "create", serializer.instance)


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

class StudyArticleViewSet(viewsets.ModelViewSet):

    serializer_class = StudyArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArticlePagination

    def get_queryset(self):
        queryset = StudyArticle.objects.all()

        return queryset

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

class StudyFieldListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = StudyArticleStudyField.objects.all()
    serializer_class = StudyArticleStudyFieldSerializer

    # override 복붙
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return DefaultResponse(serializer.data)

class LikeArticleToggleView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    # spring 같으면 DI를 이용할텐데 아직 장고는 테스트도 없고 사실상 거의 이곳에서만 해당 서비스를 이용하다보니
    # DI까지 갈 필요성은 적어보임.
    like_article_service = LikeArticleService()

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
            try:
                self.like_article_service.like(id, username)
                return DefaultResponse(True, status=201)
            except LikeArticleException as e:
                traceback.print_exc(e)
                return DefaultResponse(False, status=400, message="좋아요 생성을 실패했습니다. " + e.message)
            except Exception as e:
                traceback.print_exc(e)
                return DefaultResponse(False, status=503, message="좋아요 생성 도중 알 수 없는 에러가 발생했습니다.")
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

class BookmarkStudyArticleToggleView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id: str, format=None):
        """
        좋아요를 토글한다.
        :param request:
        :param format:
        :return:
        """
        username = request.user.username
        bookmarks = BookmarkStudyArticle.objects.filter(user_id=username, study_article_id=id)

        if StudyArticle.objects.filter(id=id, author_id=username).exists():
            return DefaultResponse(False, message="자신의 게시물은 북마크할 수 없습니다.", status=400)
        if len(bookmarks) == 0:
            s = BookmarkStudyArticleSerializer(data={"study_article": id, "user": username})
            is_valid = s.is_valid()

            if is_valid:
                s.save()
                return DefaultResponse(True, status=201)
            else:
                return DefaultResponse(False, message=str(s.errors), status=400)
        else:
            bookmarks.delete()
            return response.Response(status=204)

class ArticleTagViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleTagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        followed = self.request.query_params.get('followed', False) #  내가 follow 중인 tag
        if followed:
            following_tag_names = FollowArticleTag.objects.filter(user__username=self.request.user.username).values('tag__name')
            return ArticleTag.objects.filter(name__in=following_tag_names)

        return ArticleTag.objects.all()

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


class FollowArticleTagView(views.APIView):
    serializer_class = FollowArticleTagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FollowArticleTag.objects.filter(user=self.request.user)

    # toggle follow
    def patch(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return DefaultResponse(data=None, status=status.HTTP_204_NO_CONTENT)
        else:
            s = self.serializer_class(data={
                'user': request.user.username, 'tag': kwargs.get('tag_name')
            })
            s.is_valid(raise_exception=True)
            s.save()
            return DefaultResponse(data=None, status=status.HTTP_201_CREATED)