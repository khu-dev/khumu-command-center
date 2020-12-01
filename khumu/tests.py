import random
import time

# from django.test import TestCase
from unittest import TestCase
from article.models import Article, LikeArticle, BookmarkArticle
from user.models import KhumuUser
from comment.models import Comment, LikeComment
from board.models import Board
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

# Create your tests here.
class InitializeTest(TestCase):
    users = [
        ("admin", "관리자"), ("jinsu", "찡수"), ("gusrl4025", "꿀주먹"), ("somebody", "썸바디"), ("david", "다비드 or 데이빗"),
        ("Park", "박씨"),  ("kim", "김씨"), ("haley", 'haley'), ("mike", "mike"),  ("justin", 'justin')
    ]
    article_titles = ["미팅 잡다가", "새로운 생명체 인공지능 13주차 과제", "물및실2 교수님", "인공지능 예술", "이번 학기 대면 시험", "학원 알바 해보신 분",
                      "왜 이렇게 대면이냐 비대면이냐 정하질 못해", "이캠퍼스 강의 듣는 거", "현장실습 합격 통지 받으신 분", "코딩 도와줄 컴공 능력자분 모심",
                      "꿀알바 추천 좀", "방학 때 본가 내려가냐 마냐 그것이 문제로다", "요즘 스타트업 보시는 분??", "넷플릭스 추천 좀", "심심행~!"]
    article_bodies = [
        '''khuwitch는 다국어 번역 지원하며, 이를 음성으로도 들을 수 있도록해주는 twitch bot 입니다.
khuwitch를 이용하면 채널 관리자는 자신의 채널의 외국어 채팅을 한국어로 바로 번역해 볼 수 있고, 필요한 경우 이를 음성파일로 변환하여 재생한 뒤 시청자들에게 송출할 수도 있습니다.''',
        '''로그인 화면 추후 추가.png 봇 입장 화면 추후 추가.png
채널관리자는 twitch login을 통해 khuwitch bot을 자신의 Twitch 채널에 입장시킬 수 있습니다.
번역 화면 추가.png''',
        '''(서울=연합뉴스) 황재하 최재서 기자 = 한진그룹 조원태 회장과 대주주 연합인 이른바 `3자 연합'(주주연합) 사이 경영권 분쟁에서 법원이 또 다시 조 회장과 현 경영진의 손을 들어줬다.
이번 결정은 법원이 조 회장과 경영권 분쟁을 벌여온 3자 연합의 이익 침해 주장보다는 합병을 통한 항공산업 재편의 필요성과 이를 달성하기 위한 경영상 판단을 존중한 결과로 해석된다.
3자 연합은 지난 3월 한진칼 주주총회 의결권을 둘러싼 법정 공방에서 고배를 마신 데 이어 이번 한진칼 유상증자를 둘러싼 가처분에서도 완패했다.''',
        '''유상증자가 진행되면 3자 연합의 지분율이 약해지고 경영권 분쟁에서 불리해진다는 주장에 대해서도 재판부는 "신주 발행이 한진칼 지배권 구도를 결정적으로 바꾼다고 볼 수 없다"며 받아들이지 않았다.

재판부는 "산은이 한진칼 경영진 의사대로 의결권을 행사하겠다고 약정한 바 없고, 산은은 앞으로 항공산업의 사회경제적 중요성과 건전한 유지를 최우선으로 고려해 의결권을 행사할 것"이라고 판단했다.''',
        '''이날 KCGI의 가처분을 기각한 재판부는 앞서 지난 3월 24일에도 3자 연합이 낸 의결권 관련 가처분을 기각한 바 있다. 당시 KCGI는 대한항공 자가보험과 사우회의 의결권을 제한해달라는 가처분을 신청했지만, 재판부는 이를 기각했다.''',
        '''이날 보아는 20주년을 묻는 소감에 "나도 어색하다. 20주년이라는 말 자체가 거창한 말이라서 실감이 안 난다. 올해 굉장히 많은 분께 축하도 받았고 이벤트도 많았다. 나도 '20주년이에요'라고 말하면서 어색하다. 댄서 중에 띠동갑 차이가 나는 어린 친구들이 들어왔을 때 '내가 오래 하고 있구나'라는 생각은 들었다"라고 미소 지었다.
''',
        '''보아는 "나보다 내 주변 분들이 의미 부여를 한다. 내 입장에서도 고민이 많았다. '20주년 다운 앨범이 뭘까?' 생각했을 때, 20주년을 맞은 내가 하고 싶은 음악이 그런 앨범이지 않을까 했다. 가벼운 마음으로 임하고 있다. 나까지 무겁게 의미를 부여하면 앨범이 무거워서 세상에 안 나올 것 같다"라고 말했다.
''',
        '''"K팝의 발전을 위해 고민하는 것이 임무가 아닐까 한다."
'아시아의 별' 가수 보아가 20주년 앨범으로 돌아온다. 정상의 자리에서도 책임감과 사명감을 강조한, 역시 '넘버원' 가수는 달랐다.
1일 오전 보아의 20주년을 기념해 선보이는 정규 10집 앨범 '베터'(BETTER)의 온라인 기자간담회가 열렸다.''',
        '''보아는 "타이틀곡이 유영진 이사님 노래다. 1집 '아이디: 피스 비'가 유영진 오빠가 작사, 작곡한 노래다. 그때 나랑 유영진 오빠, 이수만 선생님 셋이서 얘기를 많이나눴다. 불과 어제까지 이수만 선생님이랑 지지고 볶았다. 우리들은 자타공인 톰과 제리가 됐다. 이렇게 세 명이 모여서 으쌰으쌰 했던 것이 감사하고 나의 데뷔 시절이 떠올라 의미가 있다"라고 돌이켰다.''',
        '''타이틀곡 '베터'는 곡을 이끄는 묵직한 베이스와 후렴구의 폭발적인 비트가 인상적인 R&B 댄스 장르의 곡이다. 망설이지 말고 당당하게 사랑을 쟁취하자는 가사를 보아의 파워풀하면서도 절제된 보컬로 표현, 압도적인 카리스마를 느낄 수 있다.''',
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
        Board(name="recent", category="logical", display_name="최근게시판", description="").save()
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
        for i, title in enumerate(self.article_titles):
            # 0,1,2번째 게시물만 default, 나머진 global
            board_id = "temporary" if i < 3 else "free"
            article = Article(board_id=board_id, title=title[:300], author_id=random.choice(users).pk,
                              content=random.choice(self.article_bodies), kind="anonymous" if i % 2 == 0 else "named")
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

        print("Create bookmark articles")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            article = random.choice(Article.objects.all())
            if article.author_id != user.username:
                bookmark_article = BookmarkArticle(article_id=article.id, user_id=user.username)
                bookmark_article.save()
            print(user.username, "bookmarks", article.id, "th article")


        print("Create like articles")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            article = random.choice(Article.objects.all())
            if article.author_id != user.username:
                like_article = LikeArticle(article_id=article.id, user_id=user.username)
                like_article.save()
            print(user.username, "likes", article.id, "th article")

        print("Create like comments")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            comment = random.choice(Comment.objects.all())
            if comment.author_id != user.username:
                likeComment = LikeComment(comment_id=comment.id, user_id=user.username)
                likeComment.save()
            print(user.username, "likes", comment.id, "th comment")