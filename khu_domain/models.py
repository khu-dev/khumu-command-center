from django.db import models
# Create your models here.
from khumu import settings
from user.models import KhumuUser


class Campus(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 단과대
class Organization(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 학과
class Department(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 비슷한 Lecture들을 덩어리지은 것.
class LectureSuite(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    course_credit = models.IntegerField()
    school_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 개별 Lecture
# 개별 Lecture를 만들기 전에 Lecture suite 데이터를 만들어줘야함.
class Lecture(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    lecture_suite = models.ForeignKey(LectureSuite, on_delete=models.CASCADE, null=True, blank=True)
    professor = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

class HaksaSchedule(models.Model):
    starts_at = models.DateTimeField(auto_now_add=False, null=False, blank=False)
    ends_at = models.DateTimeField(auto_now_add=False, null=False, blank=False)
    title = models.CharField(max_length=64, null=False, blank=False)
    # 해당 학사일정에 대한 알림이 보내졌는가
    is_notified = models.BooleanField(null=False, blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

class ConfirmHaksaSchedule(models.Model):
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False)
    haksa_schedule = models.ForeignKey(HaksaSchedule, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
