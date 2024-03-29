from django.db import models
from khu_domain.models import Department, LectureSuite, Subject
from user.models import KhumuUser
from cacheops import invalidate_obj

# Create your models here.
from khumu import settings

# category가 recent, my, bookmarked, liked, commented 게시판은 view 단에서 따로 쿼리하기
# category가 temporary인 게시판은 운영진만 보는 임시 게시판이다.

# client는 ?board=recent와 같이 이용하지만, backend에 실제로 recent라는 게시판은 존재하지 않는다.
class Board(models.Model):
    name = models.CharField(max_length=64, null=False, primary_key=True) # this is in english
    display_name = models.CharField(max_length=64, null=False)
    description = models.CharField(max_length=150, null=True, blank=True)
    admin = models.ForeignKey(KhumuUser, on_delete=models.SET_NULL, null=True, blank=True)
    campus = models.CharField(max_length=32, null=True, blank=True, default="global")  # (global | seoul | common)
    # category가 logical인 경우엔 직접 article이 참조하는 것이 아니라, business logic에 따라 article을 조회한다.
    # 예를 들어 name=bookmarked, category=logical인 경우 board의 article 조회 시 내가 북마크한 게시물만 가져옴.
    category = models.CharField(max_length=32, null=False, blank=False, default="free")  # e.g. (department | lecture_suite | free | temporary, announcement)
    related_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    related_lecture_suite = models.ForeignKey(LectureSuite, on_delete=models.SET_NULL, null=True, blank=True)
    related_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

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

    # one to many, many to one 등은 캐시 invalidation을 해주는 것이 안전하다..
    # .filter()는 잘 동작하는 것 같은데
    # .exclude)(로 조회할 땐 cache가 동작하지 않는 것 같음...ㅜㅜ
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        invalidate_obj(self.board)

    def delete(self, using=None, keep_parents=False):
        super().delete()
        invalidate_obj(self.board)