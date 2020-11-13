from comment.models import Comment
from rest_framework import serializers


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['url', 'article', 'kind', 'author', 'content', 'created_at', 'parent']


