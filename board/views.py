from board.models import Board, FollowBoard
from rest_framework import viewsets, status, permissions
from board.serializers import BoardSerializer, FollowBoardSerializer
from rest_framework import  mixins, response
from article.serializers import ArticleSerializer
from rest_framework.serializers import SerializerMethodField
from khumu.permissions import OpenPermission, is_author_or_admin
from khumu.response import DefaultResponse

MAX_ARTICLE_PREVIEW = 5

class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Board는 특이하게 UnAuthenticated도 읽을 수 있다.
    serializer_class = BoardSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category', '')
        if category:
            return Board.objects.filter(category__in=category.split(","))
        return Board.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # skip pagination
        serializer = self.get_serializer(queryset, many=True)
        serialized_boards = serializer.data
        return DefaultResponse(serialized_boards)

    def _hide_author(self, board_article, request_username):
        if board_article.author == request_username: board_article.author = "익명"

class FollowBoardViewSet(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = FollowBoardSerializer

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return FollowBoard.objects.filter(board_id=board_name)

    def create(self, request, *args, **kwargs):
        print(kwargs)
        # foreignkey field의 경우 primary key를 인자로 갖거나 그 dict에서 primary key field를 lookup한다.
        # 'user'의 value로 request.user.username와 request.user 모두 가능.
        serializer = self.get_serializer(data={'board': kwargs['board_name'], 'user': request.user.username})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DefaultResponse(None, request.user.username + " followed the board named " + kwargs['board_name'])

    # 여러 instance를 destroy 하는 경우는 delete 를 이용한다.
    def delete(self, request, *args, **kwargs):
        instances = self.get_queryset()
        print(instances)
        instances.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)