from board.models import Board
from rest_framework import viewsets
from rest_framework import permissions
from board.serializers import BoardSerializer
from rest_framework import  mixins, response
from article.serializers import ArticleSerializer
from rest_framework.serializers import SerializerMethodField
from khumu.permissions import OpenPermission, IsAuthorOrAdmin
MAX_ARTICLE_PREVIEW = 5

class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [OpenPermission]
    def get_queryset(self):
        boards = Board.objects.all()
        return boards

    serializer_class = BoardSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # skip pagination
        serializer = self.get_serializer(queryset, many=True)
        serialized_boards = serializer.data

        return response.Response(serialized_boards)

