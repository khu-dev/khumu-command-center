import json
import logging

import pytz
import requests as requests

from article.models import Article, LikeArticle, BookmarkArticle, ArticleTag, FollowArticleTag, BookmarkStudyArticle, \
    StudyArticle
from message import publisher
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer
from rest_framework import serializers
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.request import Request
from comment.serializers import CommentSerializer
from khumu import settings, config
import datetime, time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ArticleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTag
        fields = ['name', 'followed']

    followed = serializers.SerializerMethodField()

    def get_followed(self, tag_instance:ArticleTag):
        return FollowArticleTag.objects.filter(
            tag__name=tag_instance.name,
            user__username=self.context['request'].user.username
        ).exists()

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'board_name', 'board_display_name', 'title', 'author', 'is_author', 'kind',
                  'content', 'tags', 'images', 'comment_count', 'created_at',
                  'liked', 'like_article_count',
                  'bookmarked', 'bookmark_article_count']
        # depth = 3
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    author = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()
    board_display_name = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_article_count = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    bookmark_article_count = serializers.SerializerMethodField()
    tags = ArticleTagSerializer(read_only=True, many=True)

    # author = KhumuUserSimpleSerializer()
    # article의 경우 웬만해선 comment count가 필요하다.
    # db column을 serializer method로 override하면 create, update 시에 수동 기입 해줘야함.
    # 근데 아직은 body를 parse하는 방법은 application/json밖에 구현안함.
    def create(self, validated_data):
        request_user = self.context['request'].user
        body = json.loads(self.context['request'].body)
        board_name = body.get("board")
        # json field ref: https://docs.djangoproject.com/en/dev/releases/3.1/#jsonfield-for-all-supported-database-backends
        image_file_names_str = json.dumps(body.get("images"))
        tag_names = list(map(lambda tag_data: tag_data['name'], body.pop("tags", [])))

        article = Article(**validated_data, author_id=request_user.username, board_id=board_name)
        article.save()  # 우선은 저장을 해서 Article을 생성해야 tag 와의 many to many 관계를 생성 가능

        # Article과 Tag의 관계
        for tag_name in tag_names:
            ArticleTag.objects.get_or_create(name=tag_name)
        tags = []
        for tag_instance in ArticleTag.objects.filter(name__in=tag_names):
            tags.append(tag_instance)
        article.tags.set(tags)
        # many to many 관계 생성 후 다시 save
        article.save()

        return article

    def update(self, instance, validated_data):
        body = json.loads(self.context['request'].body)
        board_name = body.get("board")
        tag_names = list(map(lambda tag_data: tag_data['name'], body.pop("tags", [])))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        setattr(instance, 'board_id', board_name)

        for tag_name in tag_names:
            ArticleTag.objects.get_or_create(name=tag_name)
        tags = []
        for tag_instance in ArticleTag.objects.filter(name__in=tag_names):
            tags.append(tag_instance)
        instance.tags.set(tags)

        instance.save()
        return instance

    def get_author(self, obj):
        request_user = self.context['request'].user
        author_data = {
            "username": obj.author.username,
            "nickname": obj.author.nickname,
            "state": obj.author.state
        }
        if obj.kind == "anonymous":
            author_data['username'] = '익명'
            author_data['nickname'] = '익명'

        return author_data

    def get_is_author(self, obj):
        request_user = self.context['request'].user
        if request_user.username == obj.author.username:
            return True
        else: return False

    def get_board_name(self, obj):
        # print(self.context['request'])
        return obj.board.name

    def get_board_display_name(self, obj):
        # print(self.context['request'])
        return obj.board.display_name

    def get_tags(self, obj):
        return map(lambda tag: tag.name, obj.tags.all())

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



class ArticleDetailSerializer(ArticleSerializer):
    class Meta:
        model = Article
        fields = ArticleSerializer.Meta.fields + ['is_subscribed']

    is_subscribed = serializers.SerializerMethodField()

    notification_service_root = settings.NOTIFICATION_SERVICE.get("root")

    def get_is_subscribed(self, obj):
        request_username = self.context['request'].user.username
        print(f'Notification 서비스에 요청자가 해당 Article을 구독 중인지 조회합니다. {self.notification_service_root}subscriptions/{request_username}/article/{obj.id}')
        response = requests.get(f'{self.notification_service_root}subscriptions/{request_username}/article/{obj.id}')
        try:
            if response.status_code != 200:
                logger.error(f'Notification 서비스에 대한 요청의 status code가 200이 아닙니다. status_code={response.status_code}')
                raise self.NotificationServiceUnavailableException()
            data = json.loads(response.text)
            '''
            {
                "message": null,
                "data": {
                    "resource_id": 179,
                    "resource_kind": "article",
                    "subscriber": "jinsu",
                    "is_activated": true
                }
            }
            '''
            is_activated = data.get('data').get("is_activated")
            logger.info(f'리소스 조회 결과 {data.get("data")}')
            return is_activated
        except self.NotificationServiceUnavailableException:
            return False
        except Exception as e:
            logger.error(e)
            return False
        return False

    class NotificationServiceUnavailableException(Exception):
        pass

class StudyArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StudyArticle
        fields = ['id', 'study_board_name', 'study_board_display_name', 'title', 'author', 'is_author', 'kind',
                  'content', 'images', 'comment_count', 'created_at',
                  'bookmarked']
        # depth = 3
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    author = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    study_board_name = serializers.SerializerMethodField  ()
    study_board_display_name = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()

    # author = KhumuUserSimpleSerializer()
    # article의 경우 웬만해선 comment count가 필요하다.
    # db column을 serializer method로 override하면 create, update 시에 수동 기입 해줘야함.
    # 근데 아직은 body를 parse하는 방법은 application/json밖에 구현안함.
    def create(self, validated_data):
        request_user = self.context['request'].user
        body = json.loads(self.context['request'].body)
        study_board_name = body.get("study_board")
        # json field ref: https://docs.djangoproject.com/en/dev/releases/3.1/#jsonfield-for-all-supported-database-backends
        image_file_names_str = json.dumps(body.get("images"))

        article = StudyArticle(**validated_data, author_id=request_user.username, study_board_id=study_board_name)
        article.save()  # 우선은 저장을 해서 Article을 생성해야 tag 와의 many to many 관계를 생성 가능

        return article

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
        if obj.kind == "anonymous":
            author_data['username'] = '익명'
            author_data['nickname'] = '익명'

        return author_data

    def get_is_author(self, obj):
        request_user = self.context['request'].user
        if request_user.username == obj.author.username:
            return True
        else: return False

    def get_study_board_name(self, obj):
        # print(self.context['request'])
        return obj.study_board.name

    def get_study_board_display_name(self, obj):
        # print(self.context['request'])
        return obj.study_board.display_name

    def get_bookmarked(self, obj):
        return len(obj.bookmarkstudyarticle_set.filter(user_id=self.context['request'].user.username)) != 0

    # obj는 Article instance이다.
    def get_comment_count(self, obj):
        # print(self.context['request'])
        return len(obj.comment_set.filter(article__pk=obj.pk))

    def get_created_at(self, obj):
        return get_converted_time_string(obj.created_at)

    def publish_article_created_message(self, article):
        publisher.publish({
            'title': f'{article.title[:10]}...이 새로 작성되었습니다.',
            'content': f'ㅎㅎㅎㅎㅎ읽어주삼',
        }, 'tutorial')

class LikeArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeArticle
        fields = ['article', 'user']

class BookmarkArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkArticle
        fields = ['article', 'user']
class BookmarkStudyArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkStudyArticle
        fields = ['study_article', 'user']

class FollowArticleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowArticleTag
        fields = '__all__'
        extra_kwargs = {'user': {'required': True}, 'tag': {'required': True}}

# datetime.datetime type의 시각을 받아서 쿠뮤에서 원하는 형태의 시각으로 변환한다.
def get_converted_time_string(t:datetime.datetime):
    t = t.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

    now = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    delta = now - t
    delta_minutes = delta.seconds // 60
    # print(t.strftime("%y/%m/%d %H:%M")) # => 한국 시간으로 잘 나온다.
    if delta_minutes < 5:
        return "지금"
    elif delta_minutes < 60:
        return str(delta_minutes) + "분 전"
    elif t.year == now.year and t.month == now.month and t.day == now.day:
        return t.strftime("%H:%M")
    elif t.year == now.year:
        return t.strftime("%m/%d %H:%M")

    return t.strftime("%y/%m/%d %H:%M")
