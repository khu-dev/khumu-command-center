import logging

from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework import response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import *
from job.base_khu_job import BaseKhuException
from job.khu_auth_job import KhuAuthJob, Info21AuthenticationUnknownException
from khumu.response import *
from user.serializers import KhumuUserSerializer, GroupSerializer
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class KhumuUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'admin' in map(lambda g: g.name, request.user.groups.all()):
            return True
        else:
            if request.method == 'POST' or request.method == 'GET': return True
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                if request.parser_context['kwargs']['pk'] == 'me': return True
                elif request.parser_context['kwargs']['pk'] == request.user.username : return True
                else: return False
        return False

class KhumuUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = KhumuUser.objects.all().order_by('-created_at')
    serializer_class = KhumuUserSerializer
    permission_classes = [KhumuUserPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            for e in serializer.errors.values():
                return DefaultResponse(data=None, message=e[-1], status=status.HTTP_400_BAD_REQUEST)
        else:
            # 인포21이 필요 없는 일반 계정 생성
            if request.data.get("kind", "") == 'normal':

                serializer.save()
                return DefaultResponse(data=serializer.data, status=status.HTTP_201_CREATED)

            # 인포21을 통한 학생 계정 생성
            else:
                try:
                    khu_auth_job = KhuAuthJob({
                        'id': request.data.get('username'),
                        'password': request.data.get('password')
                    })
                    user_info = khu_auth_job.process()
                except Info21AuthenticationUnknownException as e:
                    return DefaultResponse(data=None, message=e.message, status=500)
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

                except Exception as e:
                    logger.error(str(e))
                    return DefaultResponse(data=None, message=e.message, status=400)

                headers = self.get_success_headers(serializer.data)
                return DefaultResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return DefaultResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return DefaultResponse(None, "인증되지 않은 사용자입니다.", 401)

        self.set_pk_if_me_request(request, *args, **kwargs)
        # admin이 아닌데 남에 대한 조회:
        if self.kwargs['pk'] != request.user.username and 'admin' not in map(lambda g: g.name, request.user.groups.all()):
            return DefaultResponse(None, "해당 유저를 조회할 권한이 없습니다.", 403)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return DefaultResponse(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        self.set_pk_if_me_request(request, *args, **kwargs)
        if self.kwargs['pk'] != request.user.username:
            return DefaultResponse(None, "해당 유저를 수정할 권한이 없습니다.", 403)
        else:
            return super().partial_update(request, *args, **kwargs)

    def set_pk_if_me_request(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.kwargs[lookup_url_kwarg] == 'me':
            self.kwargs[lookup_url_kwarg] = request.user.username

    # additional views
    # ref: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
    @action(detail=True, methods=['get'], url_path='is-admin')
    def is_admin(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return DefaultResponse(None, "인증되지 않은 사용자입니다.", 401)
        self.set_pk_if_me_request(request, *args, **kwargs)
        if self.kwargs['pk'] != request.user.username and 'admin' not in map(lambda g: g.name, request.user.groups.all()):
            return DefaultResponse(None, "해당 유저를 조회할 권한이 없습니다.", 403)

        is_admin = False
        # me를 통한 자기 자신에 대한 조회인지

        if 'admin' in map(lambda group: group.name, request.user.groups.all()):
            is_admin = True

        return DefaultResponse({
            'is_admin': is_admin
        }, None, 200)




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