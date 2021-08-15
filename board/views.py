import random

from board.models import Board, FollowBoard
from rest_framework import viewsets, pagination,status, permissions
from board.serializers import BoardSerializer, FollowBoardSerializer
from rest_framework import  mixins, response
from django.db.models import Q
from khumu.response import DefaultResponse
from django.core.cache import cache

MAX_ARTICLE_PREVIEW = 5

class BoardPagination(pagination.PageNumberPagination):
    page_size = 30
    page_query_param = 'page'
    page_size_query_param = 'size'
    def get_paginated_response(self, data):
        return response.Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })

class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Board는 특이하게 UnAuthenticated도 읽을 수 있다.
    pagination_class = BoardPagination
    serializer_class = BoardSerializer

    def get_queryset(self):
        queryset = Board.objects.all()
        q = self.request.query_params.get('q', '').strip()
        category = self.request.query_params.get('category', '')
        random_sort = self.request.query_params.get('random', 'false') in ('true' or True)

        if category:
            queryset = queryset.filter(category__in=category.split(","))

        if q:
            queryset = queryset.filter(Q(display_name__contains=q) | Q(name__contains=q) | Q(description__contains=q))

        if self.request.query_params.get('followed'):
            followed = self.request.query_params.get('followed').lower()
            if followed == 'true' or 'false':
                following_boards = FollowBoard.objects.filter(user=self.request.user)
                if followed == 'true':
                    queryset = queryset.filter(followboard__in=following_boards)
                else:
                    queryset = queryset.exclude(followboard__in=following_boards)
            else:
                return DefaultResponse(None, "Supported value for query string named followed: true, but got" + self.request.query_params.get('followed'), 400)

        if random_sort:
            queryset = queryset.order_by('?')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        serialized_boards = serializer.data
        # result_board: list, serialized_boards: ReturnList
        # 정렬 순서: follow 먼저 한 것부터
        result_boards = sorted(serialized_boards, key=lambda b: (not b['followed'], b['followed_at']))
        return DefaultResponse(result_boards)

    def _hide_author(self, board_article, request_username):
        if board_article.author == request_username: board_article.author = "익명"

class FollowBoardViewSet(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = FollowBoardSerializer

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return FollowBoard.objects.filter(board_id=board_name)

    def create(self, request, *args, **kwargs):
        # foreignkey field의 경우 primary key를 인자로 갖거나 그 dict에서 primary key field를 lookup한다.
        # 'user'의 value로 request.user.username와 request.user 모두 가능.
        board_name = kwargs['board_name']
        username = request.user.username
        # 이미 follow한 경우는 pass
        if FollowBoard.objects.filter(board_id=board_name, user_id=username).exists():
            return DefaultResponse(None, username + " already followed the board named" + board_name, status=200)

        # follow 안 한 경우에만 follow 생성
        serializer = self.get_serializer(data={'board': board_name, 'user': username})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DefaultResponse(None, username + " followed the board named " + board_name, status=201)

    # 여러 instance를 destroy 하는 경우는 delete 를 이용한다.
    def delete(self, request, *args, **kwargs):
        instances = self.get_queryset()
        print('팔로우를 삭제합니다', instances)
        instances.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)