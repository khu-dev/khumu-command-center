import logging

from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework import response

from job.khu_auth_job import KhuAuthJob
from khumu.response import *
from user.serializers import KhumuUserSerializer, GroupSerializer
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
        if KhumuUser.objects.filter(username=request.data.get('username')).exists():
            return BadRequestResponse('중복된 아이디의 유저가 존재합니다.')
        khu_auth_job = KhuAuthJob()
        user_info = khu_auth_job.process({
            'id': request.data.get('username'),
            'password': request.data.get('password')
        })
        data = request.data
        data['username'] = request.data.get('username')
        data['department'] = user_info.dept
        data['student_number'] = user_info.student_num
        if user_info.verified:
            data['state'] = 'active'
        else:
            return BadRequestResponse('유저의 인증 정보가 유효하지 않습니다.')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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