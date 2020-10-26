import random
import time

# from django.test import TestCase
from unittest import TestCase
from article.models import Article
from user.models import KhumuUser
from comment.models import Comment
from board.models import Board
from django.contrib.auth.hashers import make_password

# Create your tests here.
class InitializeTest(TestCase):
    usernames = ["admin", "david","jinsu", "Park", "kim", "haley", "mike","justin"]
    sentences = [
         "Lorem Ipsum has been the industry's standard",
         "galley of type and scrambled it to make a type specimen",
         "book. It has survived ",
         "not only five centuries, but also ",
         "the leap into electronic typesetting, ",
         "remaining essentially unchanged. ",
         "It was ""popularised in the ",
         "1960s with the release of ",
         "Letraset sheets containing ",
         "Lorem Ipsum passages, and ",
         "more recently with desktop ",
         "publishing software like Aldus PageMaker",
         "including ",
        "versions of Lorem Ipsum.",
        "인간의 능히 불어 청춘은 듣기만 듣는다." "이상 얼마나 우리는 얼마나 안고, 기쁘며,",
        " 인생의 아니다. 목숨을 품으며, 그러므로 넣는 찬미를",
        "못하다 인간의 길을 보라. 청춘의 얼음에 가진 길지 찬미를",
        "그것은 아니한 봄바람이다. 아니더면, 있는 청춘의 인생에 황금시대다. ",
        "끓는 꾸며 위하여 가치를 것이다. 대중을 우리의 고행을 인생을",
        "때에, 있으며, 너의 보는 싶이 있다. 품으며, ",
        "보이는 눈에 인간의 끓는 사라지지 그러므로",
        "교향악이다. 풀밭에 싸인 것은 천고에",
        "청춘의 그리하였는가? 이상의 길을 속에 맺어,",
        "때문이다. 튼튼하며, 무한한 어디 그리하였는가?",

        "사람은 천자만홍이 오아이스도 방지하는" ,
        "하는 찬미를 것이다. 살 새 인생에 아니더면",
        ", 소담스러운 피어나는 하는 그리하였는가? 피가 설산에서 천자만홍이",
        "뛰노는 트고, 그들은 속잎나고,",
        "굳세게 때문이다. 찾아 귀는 창공에",
    ]

    def test_initialize(self):
        random.shuffle(self.usernames)
        random.shuffle(self.sentences)
        users = []
        articles = []
        comments = []
        for username in self.usernames:
            user = KhumuUser(username=username, password=make_password("123123"), nickname="nick"+username)
            user.save()
            users.append(user)
            print("User created. ", user)

        board = Board(short_name="봉숭아", long_name="봉숭아학당", name="bongs", description="봉숭아학당의 커뮤니티사이트")
        board.save()
        print("Board created. ", board)
        for title in self.sentences:
            article = Article(board_id=board.id, title=title, author_id=random.choice(users).pk, content=title[::-1])
            article.save()
            articles.append(article)
            print("Article created. ", article)

        for i in range(30):
            comment = Comment(
                article=random.choice(articles),
                author=random.choice(users),
                content=random.choice(self.sentences),
                parent_id=random.choice(comments).id if i//2==1 else None
            )
            comment.save()
            comments.append(comment)
            print("Comment created. ", comment)
        print(KhumuUser.objects.all())