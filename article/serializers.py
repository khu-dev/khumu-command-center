from article.models import Article, LikeArticle
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer
from rest_framework import serializers
from rest_framework.request import Request
from comment.serializers import CommentSerializer

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'board', 'title', 'author', 'kind',
                  'content', 'images', 'liked', 'comment_count', 'like_article_count', 'created_at', ]
        # depth = 3
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    author = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_article_count = serializers.SerializerMethodField()
    # author = KhumuUserSimpleSerializer()
    # article의 경우 웬만해선 comment count가 필요하다.

    def create(self, validated_data):
        request_user = self.context['request'].user
        return Article.objects.create(**validated_data, author_id=request_user.username)

    def get_author(self, obj):
        request_user = self.context['request'].user
        author_data = {
            "username": obj.author.username,
            "nickname": obj.author.nickname,
            "state": obj.author.state
        }
        if obj.kind == "anonymous" and obj.author.username != request_user.username:
            author_data['username'] = '익명'
            author_data['nickname'] = '익명'

        return author_data
    def get_board(self, obj):
        # print(self.context['request'])
        return obj.board.name

    def get_liked(self, obj):
        return len(obj.likearticle_set.filter(user_id=self.context['request'].user.username)) != 0

    # obj는 Article instance이다.
    def get_comment_count(self, obj):
        # print(self.context['request'])
        return len(obj.comment_set.filter(article__pk=obj.pk))

    def get_like_article_count(self, obj):
        return obj.likearticle_set.count()
class LikeArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeArticle
        fields = ['article', 'user']