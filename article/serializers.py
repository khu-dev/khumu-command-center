import json

import pytz

from article.models import Article, LikeArticle, BookmarkArticle
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer
from rest_framework import serializers
from rest_framework.request import Request
from comment.serializers import CommentSerializer
from khumu import settings
import datetime, time

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'board', 'title', 'author', 'kind',
                  'content', 'images', 'comment_count', 'created_at',
                  'liked', 'like_article_count',
                  'bookmarked', 'bookmark_article_count']
        # depth = 3
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    author = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_article_count = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    bookmark_article_count = serializers.SerializerMethodField()

    # author = KhumuUserSimpleSerializer()
    # article의 경우 웬만해선 comment count가 필요하다.
    # db column을 serializer method로 override하면 create, update 시에 수동 기입 해줘야함.
    # 근데 아직은 body를 parse하는 방법은 application/json밖에 구현안함.
    def create(self, validated_data):
        request_user = self.context['request'].user
        body = json.loads(self.context['request'].body)
        board_name = body.get("board")
        return Article.objects.create(**validated_data, author_id=request_user.username, board_id=board_name)

    def update(self, instance, validated_data):
        body = json.loads(self.context['request'].body)
        board_name = body.get("board")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        setattr(instance, 'board_id', board_name)
        instance.save()
        return instance

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

    def get_bookmarked(self, obj):
        return len(obj.bookmarkarticle_set.filter(user_id=self.context['request'].user.username)) != 0

    # obj는 Article instance이다.
    def get_comment_count(self, obj):
        # print(self.context['request'])
        return len(obj.comment_set.filter(article__pk=obj.pk))

    def get_like_article_count(self, obj):
        return obj.likearticle_set.count()

    def get_bookmark_article_count(self, obj):
        return obj.bookmarkarticle_set.count()

    def get_created_at(self, obj):
        return get_converted_time_string(obj.created_at)

class LikeArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeArticle
        fields = ['article', 'user']

class BookmarkArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkArticle
        fields = ['article', 'user']

# returns string
def get_converted_time_string(t:datetime.datetime):
    t = t.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

    now = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    delta = now - t
    delta_minutes = delta.seconds // 60
    if delta_minutes < 5:
        return "지금"
    elif delta_minutes < 60:
        return str(delta_minutes) + "분 전"
    elif t.day == now.day:
        return t.strftime("%H:%M")
    elif t.year == now.year:
        return t.strftime("%m/%d %H:%M")

    return t.strftime("%y/%m/%d %H:%M")
