from django.db import models

from khu_domain.models import Department, LectureSuite
from user.models import KhumuUser
# Create your models here.
from khumu import settings

# category가 recent, my, bookmarked, liked, commented 게시판은 view 단에서 따로 쿼리하기
# category가 temporary인 게시판은 운영진만 보는 임시 게시판이다.

# client는 ?board=recent와 같이 이용하지만, backend에 실제로 recent라는 게시판은 존재하지 않는다.
class Board(models.Model):
    name = models.CharField(max_length=32, null=False, primary_key=True) # this is in english
    display_name = models.CharField(max_length=16, null=False)
    description = models.CharField(max_length=150, null=True, blank=True)
    admin = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    campus = models.CharField(max_length=16, null=True, blank=True, default="global")  # (global | seoul | common)
    # category가 logical인 경우엔 직접 article이 참조하는 것이 아니라, business logic에 따라 article을 조회한다.
    # 예를 들어 name=bookmarked, category=logical인 경우 board의 article 조회 시 내가 북마크한 게시물만 가져옴.
    category = models.CharField(max_length=16, null=False, blank=False, default="free")  # e.g. (department | lecture_suite | free | temporary, announcement)
    related_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    related_lecture_suite = models.ForeignKey(LectureSuite, on_delete=models.SET_NULL, null=True, blank=True)

class FollowBoard(models.Model):
    '''
    user의 board에 대한 follow 정보를 담당.
    board는 follower를 구할 필요 없다.
    board list를 조회 시 내가 follow 했는지를 알 수 있어야한다 => serializer에서 followed: (true | false)
    board list를 조회 시 내가 follow 한 순서대로 우선 정렬이 되고 나머진 아직은 이름 순(나중엔 정렬 로직을 생각해보자) => followed_at field 존재
    '''
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False, blank=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=False, blank=False)
    followed_at = models.DateTimeField(auto_now_add=True)