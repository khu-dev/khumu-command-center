import base64
import json

from django.test import TestCase, Client
from rest_framework import status

from article.models import Article
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
