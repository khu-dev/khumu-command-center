from board.models import Board
from rest_framework import serializers
from article.serializers import ArticleSerializer


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="user:khumuuser-detail")

    class Meta:
        model = Board
        fields = '__all__'
    recent_articles = serializers.SerializerMethodField('get_recent_articles')

    def get_recent_articles(self, obj):
        articles = ArticleSerializer(obj.article_set.order_by('id')[:2], many=True, context=self.context).data

        return articles

