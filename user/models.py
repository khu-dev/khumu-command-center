from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, PermissionsMixin, Group, _user_get_permissions
from django.contrib.auth import get_user_model
from django.utils import timezone
# Create your models here.

class KhumuUser(AbstractUser, PermissionsMixin):

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    USER_ID_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    username = models.CharField(max_length=10, unique=True, primary_key=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, help_text="우리학교 학생임이 인증되면 True. 현재는 기본적으로 True")
    type = models.CharField(max_length=16, default="khumu")
    nickname = models.CharField(max_length=10, default="흡혈형사")
    student_number = models.CharField(max_length=10, default="2000123123")
    memo = models.TextField(max_length=150, default="안녕, 잘 부탁해")
    created_at = models.DateTimeField(default=timezone.now)

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

    is_superuser = models.BooleanField(default=False)

    # def get_user_permissions(self, obj=None):
    #     return _user_get_permissions(self, obj, 'khumuuser')
