from board.models import Board
from rest_framework import viewsets
from rest_framework import permissions
from board.serializers import BoardSerializer
from rest_framework import  mixins, response
from article.serializers import ArticleSerializer
from rest_framework.serializers import SerializerMethodField

class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def get_queryset(self):
        boards = Board.objects.all()
        return boards

    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        MAX_ARTICLE_PREVIEW = 5
        queryset = self.filter_queryset(self.get_queryset())
        # skip pagination
        serializer = self.get_serializer(queryset, many=True)
        serializedBoards = serializer.data

        return response.Response(serializedBoards)

