from django.db import models
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
    category = models.CharField(max_length=16, null=False, blank=False, default="free")  # e.g. (department | lecture | free)
