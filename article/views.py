import urllib.parse as urlparse
from urllib.parse import parse_qs
from rest_framework import viewsets, pagination, permissions, views, status, generics
from rest_framework import response
from rest_framework.parsers import JSONParser, MultiPartParser

from article.services import LikeArticleService, LikeArticleException
from comment.models import Comment
from khumu import settings, config
import adapter.message.publisher
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse
from rest_framework.pagination import PageNumberPagination

from django.db.models import FilteredRelation, Q
from article.models import *
from board.models import *

from article.serializers import *
from user.serializers import KhumuUserSimpleSerializer

logger = logging.getLogger(__name__)
class ArticlePagination(pagination.CursorPagination):
    page_size_query_param = "size"
    page_size = 20  # 임의로 설정하느라 우선 크게 잡았음.
    ordering = '-created_at'
    def get_paginated_response(self, data):
        next_cursor = None
        # next_link = self.get_next_link()
        # 캐시 테스트 하느라 임시로 None
        next_link = self.get_next_link()
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

        if board_name == 'following':
            queryset = Article.objects.filter(board__followboard__user=self.request.user)
        elif board_name == 'my':
            queryset = self.request.user.article_set.filter(~Q(board__category__exact='temporary'))
        elif board_name == 'liked':
            queryset = Article.objects.filter(likearticle__in=LikeArticle.objects.filter(user=self.request.user))
        elif board_name == 'bookmarked':
            queryset = Article.objects.filter(bookmarkarticle__in=BookmarkArticle.objects.filter(user=self.request.user))
        elif board_name == 'commented':
            queryset = Article.objects.filter(comment__in=Comment.objects.filter(author=self.request.user))
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

    # view에서 실제 저장을 할 때 수행할 동작
    def perform_create(self, serializer: ArticleSerializer):
        super().perform_create(serializer)
        if settings.SNS['enabled']:
            adapter.message.publisher.publish("article", "create", serializer.instance)

    def list(self, request, *args, **kwargs):
        start = time.time()
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            logger.info(f'{self.__class__.__name__}.list() 소요시간 {time.time() - start}')
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        logger.info(f'{self.__class__.__name__}.list() 소요시간 {time.time() - start}')
        return DefaultResponse(data)

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
                traceback.print_exc()
                return DefaultResponse(False, status=400, message="좋아요 생성을 실패했습니다. " + e.message)
            except Exception as e:
                traceback.print_exc()
                return DefaultResponse(False, status=503, message="좋아요 생성 도중 알 수 없는 에러가 발생했습니다.")
        else:
            for instance in likes:
                instance.delete()
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
            for instance in bookmarks:
                instance.delete()
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
            for instance in bookmarks:
                instance.delete()
            return response.Response(status=204)
