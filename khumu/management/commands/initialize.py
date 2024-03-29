from django.core.management.base import BaseCommand, CommandError
import os
import random
import time

# from django.test import TestCase
from unittest import TestCase
from article.models import Article, LikeArticle, BookmarkArticle
from user.models import KhumuUser
from comment.models import Comment, LikeComment
from board.models import Board, FollowBoard
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = '쿠뮤의 전체적인 초기화 데이터를 구축합니다. DB와 연결되어있는지 확인해주세요~!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        initializer = Initializer()
        initializer.initialize()


# 쿠뮤의 초기화를 수행
class Initializer:
    users_data = [
        ("admin", "관리자"), ("jinsu", "찡수"), ("honeypunch123", "꿀주먹"), ("somebody", "썸바디"), ("david", "다비드 or 데이빗"),
        ("Park", "박씨"),  ("kim", "김씨"), ("haley", 'haley'), ("mike", "아임 마이크"),  ("justin", 'justin'), ('chemical', "화공과 유령"), ('computer', '컴퓨터귀신'),
        ("jo", '조교님'), ('pro', '전문가'), ("marhead", "치후닝"), ("ohayo", "오하요오하영"), ("haryeong", "하령하령"), ("1seok2", "원석원석")
    ]

    articles_data = [
        {
            "board": "department_computer_engineering",
            "title": "아옹~ 현기랑 치후니가 찡찡거려서 쿠뮤 홍보 포스터 만들어줬다~", "content": "맘에 들게 나와서 뿌듯.. 현기야 고마운 줄 알아라 알았징~?\n - 오하요오하0410영 -",
            "comments": [{
                "content": "ㅋㅋㅋㅋ 고생했으~",
            },{
                "content": "땡큐 땡큐~",
            },{
                "content": "쿠뮤 새해 복 많이~ 번창하거라~!",
            },{
                "content": "뛰어나고 재밌는 iOS 개발자분 기다립니다..!",
            }],
        },
        {
            "board": "free",
            "title": "방에서 술이 답인가?", "content": "어케 생각",
            "comments": [{
                "content": "그래 마니 마셔 난 셤공해야함..",
            }],
        },
        {
            "board": "free",
            "title": "내가 말이야", "content": "갑자기 너무 어린애 같고 어린애는 맞지만, 또 착하면 사람이 바보인 건 아니지??",
            "comments": [{
                "content": "착한사람이 바보되기는 쉬운 사회긴하지",
            },{
                "content": "바보는 아님",
            },{
                "content": "첨보는 사람한테 싸가지 없지만 않으면",
            },{
                "content": "힘내",
            },{
                "content": "힘내랏!",
            }],
        },
        {
            "board": "free",
            "title": "시사 영어", "content": "진짜로 F 주기도 하나요?",
            "comments": [{
                "content": "당연하져 ㅋㅋㅋ",
            },{
                "content": "ㅋㅋ 시험 너무 못보면 F죠 ㅜㅜ",
            },{
                "content": "저 F 였음. 근데 재수강 걍 안함 ㅜㅜ",
            },{
                "content": "그 과목 어때요?? 댓글 좀",
            }],
        },
        {
            "board": "free",
            "title": "디자인 과 분들 계심??", "content": "하나 조언 좀 구하고싶은데,,,",
            "comments": [{
                "content": "저요~! 뭔데요??",
            },{
                "content": "나를 찾지 말라.",
            },{
                "content": "디자인 디자인 신나는 노래",
            },],
        },
        {
            "board": "free",
            "title": "스터디 카페 요즘도 하나요?", "content": "집에서 너무 공부가 안됨 ㅜㅜ 카페 가면서 바람도 좀 쐐고 상쾌하게 공부하고푼디...",
            "comments": [{
                "content": "핑계야. 그냥 앞에서 산책하고 방에 와서 공부하면 되잖아.",
            },{
                "content": "이러나 저러나 공부하는 것은 힘든 일",
            },{
                "content": "지금 댓글 쓰는 것도 너무 힘드네 손목 아픔 ㅋㅋㅋ",
            },],
        },
        {
            "board": "free",
            "title": "CU 편의점에서 도시락 추천 좀", "content": "자취하니까 먹을 게 없당.",
            "comments": [{
                "content": "샌드위치가 간편하고 맛있던데",
            }, {
                "content": "계란밥머겅",
            },],
        },
        {
            "board": "free",
            "title": "태블릿 관련 질문", "content": '''갤럭시탭 A 3년전 모델을 2년 6개월째 사용 중인데, 램이 2기가라 그런지 많이 버벅입니다

주로 노트북 쓰기 버거울 때 유튜브용, 이클래스 수업 듣기, 가끔 피피티나 pdf, 문서 작업하는 용도로 태블릿을 쓰거든요.

필기는 아날로그를 좋아해서 노트에 합니다

이 정도면 아이패드 8세대 정도 사는 거 괜찮을라나요?

아니면 그냥 이 모델 중 계속 쓰는 게 나을라나요.''',
            "comments": [{
                "content": "갤탭 A, S3급만 아니면 속도 문제는 없음. 솔직히 갤탭 A는 선넘었지... 깡통이여",
            },{
                "content": "iPad 쓰는데 필기감이 그닥",
            },{
                "content": "필기감 좋아하면 종이필름 붙이면 노트랑 비슷함.",
            },{
                "content": "제꺼 한 번 써보실? 한 번 쓰는데 5천원이긴한데,,,",
            },],
        },
        {
            "board": "free",
            "title": "소웨사 시험 공부", "content": "어떤식으로 해요 다들? 진짜 감이 안잡히는데.. 엄청쉬운 것만 아니고선 문제보면 아예 손도 못건들다가 답보면 또 이해는 되고 무한반복임 머리가 안좋아서 그런가 개스트레스임 후..",
            "comments": [{
                "content": "전공자에겐 너무나도 쉬운 길",
            },{
                "content": "전공자가 소웨사를 들을 수 있음?",
            },{
                "content": "구냥 계속 반복하면 될 것 같던데요@!",
            },],
        },
        {
            "board": "free",
            "title": "웹파 시험 공부", "content": "어떤식으로 해요 다들? 진짜 감이 안잡히는데.. 엄청쉬운 것만 아니고선 문제보면 아예 손도 못건들다가 답보면 또 이해는 되고 무한반복임 머리가 안좋아서 그런가 개스트레스임 후..",
            "comments": [{
                "content": "웹파는 솔직히 무난하지... 학점도 잘 주고.",
            },{
                "content": "아~~~~ 옛날이여~!",
            },{
                "content": "내게도 이런 코린이 시절이?!",
            },],
        },
        {
            "board": "free",
            "title": "모데카이저 정보입니다.", "content": '''리메이크 전에 비하면 나아졌다지만 전체적인 능력치는 브루저라고 하기에는 그다지 좋지 않다. 기본 공격력 수치도 낮고 불멸(W)의 체력 회복 효과 때문에 체력 재생은 최하위권이며 능력치를 강탈하는 죽음의 세계(R)의 영향력으로 체력, 방어력 능력치가 타 전사들과 견주어 봤을 때 그리 좋지 않다. [6]

기본 공격 속도는 보통이나 암흑 탄생(P) 때문에 성장 공격 속도가 최하위권이며 당연히 18레벨 공격 속도도 최하위권. 그리고 추가 이동 속도 때문에 다른 근접 전사 챔피언과 비교해 기본 이동 속도도 느린 편이다. 이마저도 너프로 전 구간 3%로 고정되어 이동 속도도 하위권. 대신 성장치는 나쁘지 않은 편이고, 패시브로 평타에 추가 마법 피해 덕에 AP 딜탱임에도 평타 딜링이 매우 강한 축에 속한다.''',
            "comments": [{
                "content": "모데 고인 관짝",
            },{
                "content": "모데모데",
            },{
                "content": "난 롤을 모대",
            },],
        },
        {
            "board": "free",
            "title": "우리학교 나무 위키 내용", "content": "누가 수정하는 거?",
            "comments": [{
                "content": "누가누가누가",
            },{
                "content": "오 누가누가누가~!",
            },],
        },
        {
            "board": "free",
            "title": "경희대 꿀팁 공모전", "content": '''■출품 기간 : 2019.11.7. ~ 2019.11.16.

■출품 방법 : QR코드로 제출 or 문의 번호로 문자 전송 시 구글폼 전달

■출품 자격 : 경희대생 누구나 가능

■출품 규격 : 주제에 맞는 글귀나 한마디를 자유롭게 표현해 주세요!

■심사방법 : 심사위원 20% + 온라인투표 40% + 오프라인투표40%
■작품 예시 : 다시 한번 생각하자: 9시 수업은 한번 생각하고 줍자
나에게 생협은 학교 생활의 보너스다!

■시상 내역 :
1등 : 빕스 외식 상품권 교환권(5만원) – 2명
2등 : 올리브영 기프트카드 3만원권 – 2명
3등 : 롯데시네마 영화관람권 2매 – 2명
4등 : 스타벅스 티라미수 세트 – 2명
5등 : 버츠비 핸드크림 + 허니립밤 – 2명
참가상 : 이디야 상품권 5천원권- 10명''',
            "comments": [{
                "content": "지난 거잖아",
            }],
        },
        {
            "board": "free",
            "title": "우리학교 나무 위키 내용", "content": "누가 수정하는 거?",
            "comments": [{
                "content": "누가누가누가",
            }, {
                "content": "오 누가누가누가~!",
            }, ],
        },
        {
            "board": "department_computer_engineering",
            "title": "컴구 강의 들어도 뭔 말인지 하나도 모르겠네.", "content": "내가 바보인건가?ㅜㅜ 제때 제때 들을 껄",
            "comments": [{
                "content": "엥 교수님 디게 좋은데,,, 인생 교수님이심. 중간중간 웃기기도 하고 ㅋㅋㅋ 전에 객프도 그 교수님거 들었는데 굳굳",
            },{
                "content": "저번 학기부턴가? 플젝 없어져서 살만 함...",
            },{
                "content": "좀 어려워도 탄탄히 하면 나중에 좋을 겨 ㅋㅋ",
            },],
        },
        {
            "board": "department_computer_engineering",
            "title": "이번 방학에 같이 코테 준비하실 분들 계신가요?", "content": "혼자하려니 좀 재미없구 어렵네욧~!",
            "comments": [{
                "content": "저요",
            },{
                "content": "저두요~!",
            },{
                "content": "저저저저저저저저저저저저라뎃",
            }],
        },
        {
            "board": "department_computer_engineering",
            "title": "공모전 같은 거 해보신 분들 후기 좀", "content": "어때요? 상 타기 많이 힘든가요? 상 못 타면 말짱 도루묵이에요??",
            "comments": [{
                "content": "케바케입니다.",
            },{
                "content": "재미삼아 몇 번 나가봄.",
            },{
                "content": "방학 때 용돈 벌이 정도?.",
            }],
        },
        {
            "board": "department_computer_engineering",
            "title": "계절학기 수학", "content": "주우신 분 계신가요??",
            "comments": [{
                "content": "",
            },{
                "content": "착한사람이 바보되기는 쉬운 사회긴하지",
            },],
        },
        {
            "board": "department_computer_engineering",
            "title": "이번 프로젝트는 성공적이다.", "content": "나라도 나의 머리를 쓰담쓰담해줘야지 ㅎㅅㅎ... 고마웡 >_< 킈킈킈",
            "comments": [{
                "content": "",
            }],
        },
        {
            "board": "department_computer_engineering",
            "title": "오토스케일링 시뮬레이션 하는데", "content": "신기하고도 재미지다.",
            "comments": [{
                "content": "",
            }],
        },
        {
            "board": "department_computer_engineering",
            "title": "컴퓨터 공학과란",
            "content": "무엇을 하는 전공인가. 어디에 속하는 전공인가.\n공대의 이름을 달고 흔히 물리를 공부하거나 공학 수학을 공부하는 공대생들과는 다르다. 사실상 수학이 필요 없다.\n애초에 이과=공대식의 사고가 이상한건가",
            "comments": [
                {
                    "content": "그냥 이럴 시간에 열심히 하잣 ㅋㅋㅋ",
                }, {
                    "content": "컴공과 조아~!",
                }, {
                    "content": "다른 과 취준하는 거 보면 답 없다 절레 절레...",
                }, {
                    "content": "뿌시뿌시",
                },
            ],
        },
        {
            "board": "department_computer_engineering",
            "title": "hell, world!",
            "content": "hello, world. 그것은 새로운 세계의 시작",
            "comments": [
                {
                    "content": "hello world",
                }, {
                    "content": "R.I.P",
                },
            ],
        },
        {
            "board": "department_computer_engineering",
            "title": "워쿠맨 재밌당.",
            "content": "일주일에 몇 편씩 마니 마니 나왔으면 좋겠어~!",
            "comments": [
                {
                    "content": "우리 학교도 나왔으면 좋겠다!!",
                }, {
                    "content": "도대체 머하느라 이따구인지 궁금해.",
                }, {
                    "content": "쿠뮤나 번창하길..",
                },
            ],
        },
        {
            "board": "department_chemical_engineering",
            "title": "화공과를 나온 것은 신의 한 수", "content": "leave.....",
            "comments": [{"content": "ㅇㅈ"},{"content": "나가서 어디감?"},
                 {"content": "댓글이"},{"content": "겁나"},{"content": "많으면"},{"content": "속도가"},{"content": "어떤지"},
                 {"content": "궁금해서"}, {"content": "테스트 해봄"}, {"content": "장고보다 훨 빠르려나?"}]
            + [{"content": "테.스.트."}] * 100
        },
        {
            "board": "department_chemical_engineering",
            "title": "선배님덜 요즘 화공과 전망이 어떤가요??", "content": "주변에 있는 화공친구들이 자꾸 컴공 소융으로 떠나요...ㅜㅜ 저도 떠나야하나요?",
            "comments": [{
                "content": "미래는 아무도 모른다.",
            }],
        },
        {
            "board": "department_chemical_engineering",
            "title": "일반화학 왜케 어렵냐", "content": "고딩때는 나름 화학 잘 했던 것 같은데 같은 내용인데도 어렵네",
            "comments": [],
        },
        {
            "board": "department_chemical_engineering",
            "title": "그만그만 연습문제는 질린다구", "content": "주말에 하루종일 연습문제만 푸는 내 인생 레전드",
            "comments": [],
        },
        {
            "board": "deleted",
            "title": "이 게시판은 임시게시판이라서", "content": "일반적으로는 보이면 안됨. 보이면 리폿 좀.",
            "comments": [],
        },
        {
            "board": "deleted",
            "title": "나 이거 삭제할거임", "content": "삭제할꺼얏!!",
            "comments": [],
        },
        {
            "board": "free",
            "title": "우와 밖에 눈 또 온다!", "content": "눈 올 때에는 오리를 키워줘야지 암 그렇구 말구",
            "comments": [{
                "content": "으앙 ㅋㅋㅋㅋ 기여워!!",
            }, {
                "content": "저거 오리 만드는 거 어디서 사??",
            }, ],
            "image": []
        },
        # image 데이터는 ./initialize.sh에 저장되어있음.
        {
            "board": "free",
            "title": "쿠뮤 제 1회 워크샵!", "content": "현기 동네 게스트룸에서 진행",
            "comments": [{
                "content": "누가누가누가",
                }, {
                    "content": "오 누가누가누가~!",
                }, {
                    "content": "냠냠이 많이 했다.",
                }, {
                    "content": "개발도 많이 했다!",
                },
            ],
            # "images": '["initial_data_workshop_1.png", "initial_data_workshop_2.png", initial_data_workshop_3.png]'
        },
        {
            "board": "free",
            "title": "쿠뮤 멤버들을 소개합니다~!",
            "content": "Go와 컨테이너를 좋아하는 우미와 현기증 날 것만 같은 dizzy, Java와 보드를 좋아하는 치훈입니다.\n디자이너 하령님과 프론트 개발자 원석님도 합류해주셨습니다~!",
            "comments": [{
                "content": "화이팅 쿠뮤~!",
            }, {
                "content": "눈누난나 개발 중~!",
            }, ],
            "images": ["jinsu.jpeg", "dizzy.jpeg", "chihoon.jpeg"]
        },
        {
            "board": "free",
            "title": "디자이너님이 오셨습니다~!",
            "content": "저희 쿠뮤의 디자인과 일부 기획을 맡아주실 디자이너님이 오셨습니다. 쨕쨕쨕~~~",
            "comments": [
                {
                    "content": "화이팅 쿠뮤~!",
                }, {
                    "content": "웰컴입니다 ㅎㅎ",
                }, {
                    "content": "반갑습니다",
                },
            ],
            "images": ["jinsu.jpeg", "dizzy.jpeg", "chihoon.jpeg"]
        },
        {
            "board": "free",
            "title": "웹 프론트 개발자분이 오셨습니다~!",
            "content": "저희 쿠뮤의 다양한 웹페이지와 앱 내의 웹뷰를 개발해주실 개발자 @1seok2 원석님께서 합류해주셨습니다. 잘 부탁드려요.",
            "comments": [
                {
                    "content": "화이팅 쿠뮤~!",
                }, {
                    "content": "웰컴입니다 ㅎㅎ",
                }, {
                    "content": "반갑습니다",
                },
            ],
            "images": []
        },
    ]

    # user는 앞의 절반의 tag를 follow, 게시판에는 임의로 태그 삽입
    article_tag_names = ['흥해라쿠뮤', '임의의태그', '익명의태그', '코끼리', '침팬지', '맘모스', '기린',
                    'docker', 'kubernetes', 'golang', '치후니', '현the기', '현기', '진수', '하령']

    # raw data가 아닌 instance를 담는 녀석들
    users = []
    articles = []
    comments = []

    def initialize(self):
        users = []
        articles = []
        comments = []

        self.initialize_groups()
        self.initialize_users()
        self.initialize_boards()
        self.initialize_follow_boards()
        self.initialize_article_tags()
        self.initialize_follow_article_tags()
        self.initialize_articles()
        self.initialize_comments()
        self.initialize_bookmark_articles()
        self.initialize_like_articles()
        self.initialize_like_comments()
        self.initialize_notifications()

    def initialize_groups(self):
        print("Create groups. If the name of group exists, pass.")
        for name in ["admin", 'normal']:
            try:
                Group(name=name).save()
            except Exception as e:
                print(e)

    def initialize_users(self):
        print("Create users", self.users_data)
        for i, user_data in enumerate(self.users_data):
            user = KhumuUser(username=user_data[0], password=make_password("123123"), student_number=str(2000101000+i), nickname=user_data[1], kind='guest')
            if not KhumuUser.objects.filter(username=user_data[0]).exists():
                if user_data[0] == 'admin':
                    user.is_superuser = True
                    user.save()
                    user.groups.add(1)
                else:
                    user.save()
                    user.groups.add(2)

            self.users.append(user)

    def initialize_boards(self):
        print("Create boards")
        Board(name="announcement", category="announcement", display_name="공지사항",
              description="경희대 관련 각종 공지사항입니다.").save()
        Board(name="temporary", category="temporary", display_name="임시게시판", description="사용자에게 공개되지 않는 기본 게시판입니다.",
              campus=None).save()
        Board(name="deleted", category="temporary", display_name="삭제 게시판",
              description="사용자에게 공개되지 않는 삭제된 게시물을 담은 게시판입니다.",
              campus=None).save()
        Board(name="free", display_name="자유게시판", description="자유로운 내용을 담은 게시판입니다.").save()

        Board(name="department_computer_engineering", category="department", display_name="컴퓨터공학과",
              description="컴퓨터공학과와 관련된 내용 담은 게시판입니다.").save()
        Board(name="department_chemical_engineering", category="department", display_name="화학공학과",
              description="화학공학과와 관련된 내용을 담은 게시판입니다.").save()
        Board(name="lecture_database", category="lecture", display_name="데이터베이스",
              description="데이터베이스 수업과 관련된 내용의 게시판입니다.").save()
        Board(name="lecture_data_center_programming", category="lecture", display_name="데이터센터프로그래밍",
              description="데이터센터프로그래밍 수업과 관련된 내용의 게시판입니다.").save()
        Board(name="lecture_calculus", category="lecture", display_name="미분적분학",
              description="미분적분 수업과 관련된 내용의 게시판입니다.").save()

    def initialize_follow_boards(self):
        print("Create follow-boards")
        for user_data in self.users_data:
            for board_name in ["free", "department_computer_engineering", "lecture_data_center_programming"]:
                FollowBoard(board_id=board_name, user_id=user_data[0]).save()
                print(f'{user_data[0]} follows Board({board_name})')

    def initialize_article_tags(self):
        print("Create article-tags")
        for tag_name in self.article_tag_names:
            print("Article-Tag name:", tag_name)

    def initialize_articles(self):
        print("Created articles")
        for i, article in enumerate(self.articles_data):
            article_instance = Article(board_id=article['board'], title=article['title'],
                                       author_id=random.choice(self.users).username,
                                       content=article['content'], kind="anonymous" if i % 2 == 0 else "named",
                                       images=article.get('images', []))
            article_instance.save()
            self.articles.append(article_instance)
            print("Article: ", article_instance)

    def initialize_comments(self):
        # 만약 article_id가 articles_data에서의 index + 1 이 아니면 엉뚱한 댓글이 사용될 수 있음!
        for article_id, article_data in enumerate(self.articles_data, 1):
            for comment in article_data['comments']:
                comment_instance = Comment(
                    article_id=article_id,
                    author_id=random.choice(self.users).username,
                    content=comment['content'],
                    parent_id=None
                )
                comment_instance.save()
                self.comments.append(comment_instance)
                print("Create random comments. ", comment_instance)

    def initialize_bookmark_articles(self):
        print("Create bookmark articles")
        for _ in range(120):
            user = random.choice(KhumuUser.objects.all())
            article = random.choice(Article.objects.all())
            if article.author_id != user.username:
                bookmark_article = BookmarkArticle(article_id=article.id, user_id=user.username)
                bookmark_article.save()
            print(user.username, "bookmarks", article.id, "th article")

    def initialize_like_articles(self):
        print("Create like articles")
        for _ in range(200):
            user = random.choice(KhumuUser.objects.all())
            article = random.choice(Article.objects.all())
            if article.author_id != user.username:
                like_article = LikeArticle(article_id=article.id, user_id=user.username)
                like_article.save()
            print(user.username, "likes", article.id, "th article")

    def initialize_like_comments(self):
        print("Create like comments")
        for _ in range(300):
            user = random.choice(KhumuUser.objects.all())
            comment = random.choice(Comment.objects.all())
            if comment.author_id != user.username:
                like_comment = LikeComment(comment_id=comment.id, user_id=user.username)
                like_comment.save()
            print(user.username, "likes", comment.id, "th comment")

    def initialize_notifications(self):
        print("Create notifications about comment")
        for comment in Comment.objects.all():
            article_id = comment.article_id
            article_author_username = comment.article.author_id
            Notification(kind='커뮤니티', title='게시물에 댓글이 달렸습니다.', content=comment.content, is_read=False, recipient_id=comment.author_id).save()
            print(f'Notification about creating comment({comment.id})')



