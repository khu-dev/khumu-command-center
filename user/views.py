import logging
import traceback

from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import *
from job.base_khu_job import BaseKhuException
from job.khu_auth_job import KhuAuthJob, Info21AuthenticationUnknownException
from khumu.response import *
from user.serializers import KhumuUserSerializer, GroupSerializer
from user.models import KhumuUser, AccessLog
from adapter.slack import slack
from adapter.message import publisher
from django.conf import settings

logger = logging.getLogger(__name__)

class KhumuUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'admin' in map(lambda g: g.name, request.user.groups.all()):
            return True
        else:
            if request.method == 'POST' or request.method == 'GET': return True
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                if request.parser_context['kwargs']['pk'] == 'me':
                    return True
                elif request.parser_context['kwargs']['pk'] == request.user.username:
                    return True
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
        serializer.save()
        instance = KhumuUser.objects.get(username=serializer.data['username'])
        if settings.SNS['enabled']:
            publisher.publish("user", "create", instance)
        slack.send_message("🌟 신규 유저 가입!", f'{instance.nickname}(id={instance.username}, student_number={instance.student_number}, department={instance.department})님이 새로 가입하셨어요.')
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
            try:
                return DefaultResponse(data=super().partial_update(request, *args, **kwargs).data, status=200)
            except ValidationError as e:
                traceback.print_exc()
                return DefaultResponse(None, next(iter(e.detail.values())), 400)

    def perform_update(self, serializer):
        serializer.save()
        instance = self.get_object()
        if settings.SNS['enabled']:
            publisher.publish("user", "update", instance)

    def destroy(self, request, *args, **kwargs):
        self.set_pk_if_me_request(request, *args, **kwargs)
        logger.info('회원을 탈퇴시킵니다.' + self.kwargs.get('pk'))
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.status = 'deleted'
        instance.save()
        slack.send_message('유저가 탈퇴했습니다.', 'ID: ' + instance.username)
        if settings.SNS['enabled']:
            publisher.publish("user", "delete", instance)

    def set_pk_if_me_request(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.kwargs[lookup_url_kwarg] == 'me':
            self.kwargs[lookup_url_kwarg] = request.user.username

    @action(detail=False, methods=['post'], url_path='verify-new-student')
    def verify_new_student(self, request, *args, **kwargs):
        users = KhumuUser.objects.filter(username=request.data.get('username'))
        if users.exists():
            u = users.first()
            if u.status == 'deleted':
                return DefaultResponse(
                    data=None,
                    message='탈퇴한 유저입니다.\n탈퇴한 유저의 재가입은 쿠뮤에 문의해주세요.',
                    status=400
                )
            return DefaultResponse(
                data=None,
                message='이미 존재하는 ID입니다.',
                status=400
            )
        job = KhuAuthJob({
            'id': request.data.get('username'),
            'password': request.data.get('password')
        })
        try:
            user_info = job.process()
            # json 직렬화를 위해 __dict__ 이용
            return DefaultResponse(data=user_info.__dict__, message=None, status=200)
        except Info21AuthenticationUnknownException as e:
            traceback.print_exc()
            return DefaultResponse(data=None, message=e.message, status=500)
        except BaseKhuException as e:
            traceback.print_exc()
            return DefaultResponse(data=None, message=e.message, status=400)

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

    @action(detail=False, methods=['post'], url_path='access')
    def access(self, request):
        access_log = AccessLog()
        if request.user.is_authenticated:
            access_log.username = request.user.username

        access_log.save()

        return DefaultResponse(data=None)

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