from django.db import models
# Create your models here.
from khumu import settings
from user.models import KhumuUser


class Campus(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# Deprecated
# 단과대
class Organization(models.Model):
    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 단과대 혹은 대학
class NewOrganization(models.Model):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=32, null=False, blank=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# Deprecated
# 학과
class Department(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 학과
class NewDepartment(models.Model):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128, null=False, blank=False)
    organization = models.ForeignKey(NewOrganization, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# Deprecated
# 비슷한 Lecture들을 덩어리지은 것.
class LectureSuite(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    course_credit = models.IntegerField()
    school_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 한 Subject는 여러 Lecture일 수 있음.
# 기존의 LectureSuite이 Subject로 개선되었다.
# 한 Subject는 한 학과와 1대1 관계도 아니기에 학과 정보도 제거했다.
class Subject(models.Model):
    code = models.CharField(max_length=32, null=False, blank=False, unique=True)
    # code는 다른데 name은 같은 과목도 있다...
    name = models.CharField(max_length=128, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# Deprecated
# 개별 Lecture
# 개별 Lecture를 만들기 전에 Lecture suite 데이터를 만들어줘야함.
class Lecture(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    lecture_suite = models.ForeignKey(LectureSuite, on_delete=models.CASCADE, null=True, blank=True)
    professor = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# Lecture
# 여러 강의가 한 Subject와 관계를 가질 수 있다.
# 한 Subject에 대해 교수가 다르거나 학기가 다르거나 학년도가 다르면 다른 강의이다.
class NewLecture(models.Model):
    code = models.CharField(max_length=32, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=False, blank=False)
    year = models.IntegerField(null=False, blank=False)
    term = models.IntegerField(null=False, blank=False)
    professor = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 학사일정을 의미
class HaksaSchedule(models.Model):
    starts_at = models.DateTimeField(auto_now_add=False, null=False, blank=False)
    ends_at = models.DateTimeField(auto_now_add=False, null=False, blank=False)
    title = models.CharField(max_length=64, null=False, blank=False)
    # 해당 학사일정에 대한 알림이 보내졌는가
    is_notified = models.BooleanField(null=False, blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

# 학사일정을 확인했는가를 의미
class ConfirmHaksaSchedule(models.Model):
    user = models.ForeignKey(KhumuUser, on_delete=models.CASCADE, null=False)
    haksa_schedule = models.ForeignKey(HaksaSchedule, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
