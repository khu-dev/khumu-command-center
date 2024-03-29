import urllib.parse as urlparse
from urllib.parse import parse_qs
from rest_framework import viewsets, pagination, permissions, views, status, generics
from rest_framework import response

from rest_framework.decorators import action
from article.services import LikeArticleService, LikeArticleException
import adapter.message.publisher
from khumu.permissions import is_author_or_admin
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse

from django.db.models import FilteredRelation, Q
from article.models import *
from board.models import *

from django.utils import timezone
import time
from article.serializers import *
from user.serializers import KhumuUserSimpleSerializer
from base64 import b64decode, b64encode
from urllib import parse
from rest_framework.pagination import replace_query_param

logger = logging.getLogger(__name__)

class ArticlePagination(pagination.PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'size'

    def get_paginated_response(self, request, data):
        return response.Response({
            'links': {
                'next': self.get_next_link(request, data),
                'previous': self.get_previous_link(request, data)
            },
            'data': data
        })
    def get_next_link(self, request, data):
        if request.query_params.get('board') != 'commented':
            return super().get_next_link()

        if len(data) == 0:
            return None
        else:
            url = request.build_absolute_uri()
            page_number = int(request.query_params.get(self.page_query_param, 1))
            return replace_query_param(url, self.page_query_param, page_number + 1)

    def get_previous_link(self, request, data):
        if request.query_params.get('board') != 'commented':
            return super().get_previous_link()

        url = request.build_absolute_uri()
        page_number = int(request.query_params.get(self.page_query_param, 1))
        if page_number == 1:
            return None
        else:
            return replace_query_param(url, self.page_query_param, page_number - 1)

class IsArticleCheckPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'is_author':
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action == 'is_author':
            return True

        else:
            return super().has_permission(request, view)

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsArticleCheckPermission]
    pagination_class = ArticlePagination

    def get_queryset(self):
        board_name = self.request.query_params.get('board')
        q = self.request.query_params.get('q', '')

        if board_name == 'following':
            queryset = Article.objects.filter(board__followboard__user=self.request.user)
        elif board_name == 'my':
            queryset = self.request.user.article_set.filter(~Q(board__category__exact='temporary'))
        elif board_name == 'liked':
            queryset = Article.objects.filter(likearticle__in=LikeArticle.objects.filter(user=self.request.user)).distinct()
        elif board_name == 'bookmarked':
            queryset = Article.objects.filter(bookmarkarticle__in=BookmarkArticle.objects.filter(user=self.request.user)).distinct()
        elif board_name == 'commented':
            print(
                f'Comment 서비스에 최근에 댓글 단 게시글 ID를 조회합니다. {settings.COMMENT_SERVICE.get("root")}comments/get-comment-count')
            try:
                response = requests.post(
                    f'{settings.COMMENT_SERVICE.get("root")}comments/get-commented-articles',
                    headers={'Authorization': self.request.META['HTTP_AUTHORIZATION']},
                    data={
                        'size': self.request.query_params.get('size', 10),
                        'page': self.request.query_params.get('page', None),
                    },
                    timeout=(1, 1)  # Connection timeout, Read timeout seconds
                )
                if response.status_code != 200:
                    logger.error(f'Comment 서비스에 대한 요청의 status code가 200이 아닙니다. status_code={response.status_code}')
                    logger.error(response.text)
                data = json.loads(response.text)
                '''
                {
                    "data": [1, 2, 4, 7, 6, ...],
                    "message": ""
                }
                '''
                article_id_list = data.get('data', [])
                queryset = Article.objects.filter(id__in=article_id_list)
                queryset = sorted(queryset, key=lambda a: article_id_list.index(a.id))
            except Exception as e:
                logger.error('Comment 서비스와 통신 중 알 수 없는 오류 발생')
                traceback.print_exc()
                raise e
        elif board_name == 'hot':
            queryset = Article.objects.filter(is_hot=True)
        elif board_name:
            queryset = Article.objects.filter(~Q(board__category__exact='temporary')).filter(board_id=self.request.query_params['board'])
        # 기본 쿼리셋
        else:
            queryset = Article.objects
        if len(q) != 0:
            queryset = queryset.filter(Q(title__contains=q) | Q(content__contains=q)).distinct()
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
            
    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(self.request, data)
    def list(self, request, *args, **kwargs):
        start = time.time()
        queryset = self.filter_queryset(self.get_queryset())
        
        if self.request.query_params.get('board', '') != 'commented':
            page = self.paginate_queryset(queryset)
            # pagination을 사용하도록 설정된 경우
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = serializer.data
                logger.info(f'{self.__class__.__name__}.list() 소요시간 {time.time() - start}')
                return self.get_paginated_response(data)
            else:
            # pagination을 사용하지 않도록 설정된 경우
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                logger.info(f'{self.__class__.__name__}.list() 소요시간 {time.time() - start}')
                return self.get_paginated_response(data)
        else:
            # commented. 즉 내가 댓글 단 게시글을 조회할 때에는 페이지네이션을 command-center가 하는 게 아니라
            # comment가 수행한다.
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            logger.info(f'{self.__class__.__name__}.list() 소요시간 {time.time() - start}')

            return self.get_paginated_response(data)

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_serialized = self.get_serializer(article).data

        return DefaultResponse(article_serialized)

    @action(methods=['POST'], detail=True, url_path='is-author')
    def is_author(self, request, *args, **kwargs):
        logger.info(f'{kwargs.get("pk")}의 author가 인자로 전달된 author가 맞는지 체크합니다.')
        article = Article.objects.get(pk=kwargs.get("pk"))
        logger.info(f'Article({kwargs.get("pk")}).username = {article.author.username}, 인자로 전달된 author = {request.data.get("author")}')
        return DefaultResponse({
            "is_author": article.author.username == request.data.get("author")
        })

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
