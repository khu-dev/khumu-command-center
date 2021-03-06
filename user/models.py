from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, PermissionsMixin, Group, _user_get_permissions
from django.contrib.auth import get_user_model
from django.utils import timezone
# Create your models here.

class KhumuUser(AbstractUser, PermissionsMixin):

    # EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    USER_ID_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    username = models.CharField(max_length=20, primary_key=True, unique=True, null=False)
    # password inherited
    # email = models.EmailField(blank=True) #

    # student는 Info21을 통해 로그인하는 종류의 유저
    # guest는 테스터 계정과 같은 종류의 유저
    # staff는 우리 관리자. 근데 지금은 필요 없긴 함.
    # organization은 학생회 같은 단체 계정
    kind = models.CharField(max_length=16, default="student", null=False) # (student | organization | staff | guest)
    nickname = models.CharField(max_length=20, unique=True, null=False)
    student_number = models.CharField(max_length=10, default="2000123123", unique=False, null=True, blank=True)
    department = models.CharField(max_length=16, default="학과 미설정", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=False)
    state = models.CharField(max_length=16, default="unverified", null=False)
    is_superuser = models.BooleanField(default=False, null=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.',
        related_name="khumuuser_set",
        related_query_name="khumuuser",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('khumuuser permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="khumuuser_set",
        related_query_name="khumuuser",
    )

    email = None
    first_name = None
    last_name = None
    is_staff = None
    # def get_user_permissions(self, obj=None):
    #     return _user_get_permissions(self, obj, 'khumuuser')
