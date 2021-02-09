import base64
import json

from django.test import TestCase, Client
from rest_framework import status

from article.models import ArticleTag, FollowArticleTag, Article
from article.serializers import FollowArticleTagSerializer
from board.models import Board
from khumu.jwt import KhumuJWTSerializer
from user.models import KhumuUser

class ArticleView(TestCase):
    board = 'sandbox'
    username = 'jinsu'
    nickname = '진수'
    tag_name = 'kubernetes'
    password = '123123'

    def setUp(self):
        Board(name=self.board).save()
        # password는 바로 주입하면 안되고, set_password를 통해 암호화해주어야한다.
        u = KhumuUser(username=self.username, nickname=self.nickname)
        u.set_password(self.password)
        u.save()

        ArticleTag(name=self.tag_name).save()

    def test_create_article(self):
        c = Client()
        c.login(username=self.username, password=self.password)
        resp = c.post(f'/api/articles',
            content_type='application/json',
            data={
                  'board': 'sandbox',
                  'title': '제목',
                  'content': '내용',
            })
        if resp.status_code != 201:
            print(resp.content)
            self.assertEqual(201, resp.status_code)
        self.assertTrue(Article.objects.filter(author__username=self.username, title='제목').exists())


class FollowArticleTagSerializerTest(TestCase):
    username = 'jinsu'
    nickname = '진수'
    tag_name = 'kubernetes'
    def setUp(self):
        KhumuUser(username=self.username, nickname=self.nickname).save()
        ArticleTag(name=self.tag_name).save()

    def test_create_follow_article_tag(self):
        s = FollowArticleTagSerializer(data={
            'user': self.username,
            'tag': self.tag_name
        })
        s.is_valid()
        self.assertEqual({}, s.errors)
        self.assertTrue(s.is_valid())
        s.create(s.validated_data)
        self.assertTrue(FollowArticleTag.objects.filter(user=self.username, tag=self.tag_name).exists())

class FollowArticleTagView(TestCase):
    username = 'jinsu'
    nickname = '진수'
    password = '123123'
    tag_name = 'kubernetes'

    def setUp(self):
        super().setUp()
        u = KhumuUser(username=self.username, nickname=self.nickname)
        u.set_password(self.password)
        u.save()

        ArticleTag(name=self.tag_name).save()

    # toggle을 통해 create
    def test_create_follow_article_tag(self):
        c = Client()
        c.login(username=self.username, password=self.password)
        resp = c.patch(f'/api/article-tags/{self.tag_name}/follows',
            content_type='application/json',
            data={}
        )
        if resp.status_code != status.HTTP_201_CREATED:
            print(resp.content)
            self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
        self.assertTrue(FollowArticleTag.objects.filter(user__username=self.username, tag=self.tag_name).exists())

    # toggle을 통해 delete
    def test_destroy_follow_article_tag(self):
        c = Client()
        c.login(username=self.username, password=self.password)

        # setup
        FollowArticleTag(user_id=self.username, tag_id=self.tag_name).save()
        self.assertTrue(FollowArticleTag.objects.filter(user_id=self.username, tag_id=self.tag_name).exists())

        # process
        resp = c.patch(f'/api/article-tags/{self.tag_name}/follows',
            content_type='application/json',
        )
        if resp.status_code != status.HTTP_204_NO_CONTENT:
            self.assertEqual(status.HTTP_204_NO_CONTENT, resp.status_code)
        self.assertFalse(FollowArticleTag.objects.filter(user__username=self.username, tag=self.tag_name).exists())

        # result
        self.assertFalse(FollowArticleTag.objects.filter(user_id=self.username, tag_id=self.tag_name).exists())
