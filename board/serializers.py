from board.models import Board
from rest_framework import serializers
from article.serializers import ArticleSerializer

class BoardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'
    recent_articles = serializers.SerializerMethodField('get_recent_articles')
    def get_recent_articles(self, obj):
        articles = obj.article_set.filter(board__name=obj.name)
        return ArticleSerializer(articles, many=True, context=self.context).data

