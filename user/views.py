import logging

from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework import response
from rest_framework.exceptions import ValidationError

from job.base_khu_job import BaseKhuException
from job.khu_auth_job import KhuAuthJob
from khumu.response import *
from user.serializers import KhumuUserSerializer, GroupSerializer, SignUpWrongValueException
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class KhumuUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if 'admin' in map(lambda g: g.name, request.user.groups.all()):
            return True
        else:
            if request.method == 'POST': return True
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                if request.user.username == request.data['username']: return True
                else: return False

class KhumuUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = KhumuUser.objects.all().order_by('-created_at')
    serializer_class = KhumuUserSerializer
    permission_classes = [KhumuUserPermission]

    def create(self, request, *args, **kwargs):
        if not request.data.get("username", "") or not request.data.get("password", ""):
            return DefaultResponse(data=None, message="아이디와 비밀번호를 입력해주세요.", status=400)

        try:
            khu_auth_job = KhuAuthJob({
                'id': request.data.get('username'),
                'password': request.data.get('password')
            })
            user_info = khu_auth_job.process()
        except BaseKhuException as e:
            return DefaultResponse(data=None, message=e.message, status=400)


        data = request.data
        data['username'] = request.data.get('username')
        data['department'] = user_info.dept
        data['student_number'] = user_info.student_num
        if user_info.verified:
            data['state'] = 'active'
        else:
            return BadRequestResponse('유저의 인증 정보가 유효하지 않습니다.')
        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        except SignUpWrongValueException as e:
            logger.error(str(e))
            return DefaultResponse(data=None, message=e.message, status=400)

        headers = self.get_success_headers(serializer.data)
        return DefaultResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return DefaultResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return DefaultResponse(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return DefaultResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return DefaultResponse(self.get_object())