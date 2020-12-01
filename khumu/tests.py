import random
import time

# from django.test import TestCase
from unittest import TestCase
from article.models import Article, LikeArticle
from user.models import KhumuUser
from comment.models import Comment, LikeComment
from board.models import Board
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

# Create your tests here.
class InitializeTest(TestCase):
    users = [
        ("admin", "관리자"), ("jinsu", "찡수"), ("somebody", "썸바디"), ("david", "다비드 or 데이빗"),
        ("Park", "박씨"),  ("kim", "김씨"), ("haley", 'haley'), ("mike", "mike"),  ("justin", 'justin')
    ]
    sentences = [
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
        """Go의 초기 디자인은 2007년 9월 21일에 로버트 그리즈머, 롭 파이크, 켄 톰프슨이 인페르노 분산 운영체제와 관련된 작업을 하다가 시작되었다. 
화이트 보드에 새로운 언어에 대한 스케치를 하면서 초기 20% 파트타임 프로젝트로 시작하였다가 2008년 1월 켄 톰프슨이 C 코드를 만들어내는 컴파일러를 만들기 시작했고, 2008년 중반 풀타임 프로젝트로 승격되었다. 2008년 5월 이안 테일러가 Go 스펙의 초안을 이용해서 GCC 프론트엔드를 만들기 시작했고, 2008년 말 러스 콕스가 참여하면서 프로토타입에서 실질적인 언어와 라이브러리들을 만들기 시작했다. 2009년 11월 10일에 리눅스와 MacOS 플랫폼을 대상으로 공식 발표되었다. Go가 처음 런칭되었을 때는 실무적인 소프트웨어를 만들기에는 준비가 좀 덜 된 상태였지만, 2010년 5월 롭 파이크는 구글에서 실제로 사용되고 있는 부분이 있다고 공개적으로 알리게 되었다. 2009년 11월에 Go가 발표되었다. 
구글의 생산 시스템 중 일부 및 기타 기업들에 사용되고 있다.[15]""",
        "Go는 다른 언어의 긍정적인 특징들을 유지하면서 공통이 되는 문제들을 해결할 새로운 프로그래밍 언어를 설계하기 위해 구글의 엔지니어 Robert Griesemer, 롭 파이크, 켄 톰프슨에 의해 실험적으로 시작되었다. 이 새로운 언어는 다음의 기능을 포함할 작정이었다:[16]",
        """정적 타이핑 및 대형 시스템으로의 스케일 가능할 것 (마치 자바와 C++처럼)
너무 많은 필수적인 키워드와 반복 없이도 생산적이고 가독성이 좋을 것[17] (동적 프로그래밍 언어와 같이 가벼움)
통합 개발 환경이 필요하지 않지만 지원도 가능할 것
네트워킹 및 다중 처리를 지원할 것""",
        "나중의 인터뷰에서, 언어 설계자 3명 모두 자신들이 C++의 복잡성을 싫어하며 이로 인해 새로운 언어를 설계하는 계기가 되었다고 언급하였다.[18][19][20]",
    ]

    def test_initialize(self):
        print("Create groups. If the name of group exists, pass.")
        for name in ["admin", 'normal']:
            try:
                Group(name=name).save()
            except Exception as e:
                print(e)

        random.shuffle(self.users)
        random.shuffle(self.sentences)
        users = []
        articles = []
        comments = []

        print("Create random users", self.users)
        for i, randomUser in enumerate(self.users):
            user = KhumuUser(username=randomUser[0], password=make_password("123123"), student_number=str(2000101000+i), nickname=randomUser[1])
            if not KhumuUser.objects.filter(username=randomUser[0]).exists():
                if randomUser[0] == 'admin':
                    user.is_superuser = True
                    user.save()
                    user.groups.add(1)
                else:
                    user.save()
                    user.groups.add(2)

            users.append(user)

        print("Create boards")
        Board(name="temporary", display_name="임시게시판", description="사용자에게 공개되지 않는 기본 게시판입니다.",
              campus=None, category="free").save()
        Board(name="free", display_name="자유게시판", description="자유로운 내용을 담은 게시판입니다.").save()
        Board(name="my", category="logical", display_name="내가 작성한 게시물", description="").save()
        Board(name="bookmarked", category="logical", display_name="북마크한 게시물", description="").save()
        Board(name="commented", category="logical", display_name="댓글단 게시물", description="").save()
        Board(name="liked", category="logical", display_name="좋아요한 게시물", description="").save()

        Board(name="computer_engineering", category="department", display_name="컴퓨터공학과",
              description="컴퓨터공학과와 관련된 내용 담은 게시판입니다.").save()
        Board(name="chemical_engineering", category="department", display_name="화학공학과",
              description="화학공학과와 관련된 내용을 담은 게시판입니다.").save()


        print("Created articles")
        for i, title in enumerate(self.sentences):
            # 0,1,2번째 게시물만 default, 나머진 global
            board_id = "temporary" if i < 3 else "free"
            article = Article(board_id=board_id, title=title[:300], author_id=random.choice(users).pk,
                              content=random.choice(self.sentences), kind="anonymous" if i % 2 == 0 else "named")
            article.save()
            articles.append(article)
            print("Article: ", article)

        for i in range(120):
            comment = Comment(
                article=random.choice(articles),
                author=random.choice(users),
                content=random.choice(self.sentences),
                parent_id=random.choice(comments).id if i//2==1 else None
            )
            comment.save()
            comments.append(comment)
            print("Create random comments. ", comment)

        print("Create like articles")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            article = random.choice(Article.objects.all())
            if article.author_id != user.username:
                likeArticle = LikeArticle(article_id=article.id, user_id=user.username)
                likeArticle.save()
            print(user.username, "likes", article.id, "th article")

        print("Create like comments")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            comment = random.choice(Comment.objects.all())
            if comment.author_id != user.username:
                likeComment = LikeComment(comment_id=comment.id, user_id=user.username)
                likeComment.save()
            print(user.username, "likes", comment.id, "th comment")