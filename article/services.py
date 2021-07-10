import datetime
import logging
import traceback

from article.models import Article, LikeArticle
from article.serializers import LikeArticleSerializer
from message.publisher import publish

logger = logging.getLogger(__name__)

class LikeArticleService:
    MINIMUM_NUMBER_OF_LIKES_FOR_HOT = 5

    def like(self, article_id:int, username:str) ->(Exception, dict):
        s = LikeArticleSerializer(data={"article": article_id, "user": username})
        is_valid = s.is_valid()
        if is_valid:
            s.save()

            article = Article.objects.get(id=article_id)
            is_hot_article = self.is_hot(article)
            # 만약 이번 좋아요로 인해 hot article이 되는 경우
            if not article.is_hot and is_hot_article:
                logger.info("커뮤니티 게시글을 좋아요하며 새로운 핫 게시글 선정. " + str(article))
                article.is_hot = True
                article.save()
                publish('article', 'new_hot_article', article)
            return s.data
        else:
            raise LikeArticleException(s.errors)

    def is_hot(self, instance: Article) -> bool:
        return instance.likearticle_set.count() >= self.MINIMUM_NUMBER_OF_LIKES_FOR_HOT


class LikeArticleException(Exception):
    def __init__(self, errors):
        self.message = errors




