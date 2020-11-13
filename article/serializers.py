from article.models import Article
from user.models import KhumuUser
from user.serializers import KhumuUserSimpleSerializer
from rest_framework import serializers
from rest_framework.request import Request
from comment.serializers import CommentSerializer

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'board', 'title', 'author', 'kind', 'content', 'images', 'created_at', 'comment_count']
        # depth = 3
        # fields = ['board', 'title', 'author', 'content', 'create_at', 'comment_count']

    comment_count = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    # author = KhumuUserSimpleSerializer()
    # article의 경우 웬만해선 comment count가 필요하다.
    def get_comment_count(self, obj):
        # print(self.context['request'])
        return len(obj.comment_set.filter(article__pk=obj.pk))

    def get_author(self, obj):
        request_username = self.context['request'].user.username
        author = KhumuUser.objects.get(username=obj.author)
        # author_simple_serialized = KhumuUserSimpleSerializer(data={
        #     "username": author.username,
        #     "state": author.state,
        # }, many=False, context=self.context)
        author_data = {
            "username": author.username,
            "state": author.state,
        }
        if obj.kind == "anonymous" and author.username != request_username:
            author_data['username'] = '익명'

        return author_data
