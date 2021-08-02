from board.models import Board, FollowBoard
from rest_framework import serializers
from article.serializers import ArticleSerializer, StudyArticleSerializer


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="user:khumuuser-detail")

    class Meta:
        model = Board
        fields = ['name', 'category', 'display_name', 'description', 'followed', 'followed_at']
        ordering = ('followed',)
        order_by = ('followed',)

    followed = serializers.SerializerMethodField()
    followed_at = serializers.SerializerMethodField()


    def get_followed(self, obj):
        return FollowBoard.objects.filter(board_id=obj.name, user_id=self.context['request'].user.username).exists()

    def get_followed_at(self, obj):
        if self.get_followed(obj):
            return FollowBoard.objects.filter(board_id=obj.name, user_id=self.context['request'].user.username).first().followed_at
        return None

class FollowBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowBoard
        fields = ['board', 'user']