from article.models import Article
from rest_framework import serializers
from rest_framework.request import Request
from comment.serializers import CommentSerializer

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['url', 'board', 'title', 'author', 'content', 'images', 'create_at', 'comment_count']
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    comment_count = serializers.SerializerMethodField()

    # article의 경우 웬만해선 comment count가 필요하다.
    def get_comment_count(self, obj):
        # print(self.context['request'])
        return len(obj.comment_set.filter(article__pk=obj.pk))

