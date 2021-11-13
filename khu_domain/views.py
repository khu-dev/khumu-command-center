import logging
import time
from django.utils import timezone
from django.conf import settings
import traceback
from rest_framework.decorators import action
from rest_framework import viewsets, pagination, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import generics

import adapter.message.publisher
import adapter.slack.slack
from job.khu_lecture_sync import KhuLectureSyncJob
from khu_domain.models import LectureSuite, Organization, HaksaSchedule, Department, ConfirmHaksaSchedule
from khu_domain.serializers import LectureSuiteSerializer, OrganizationSerializer, HaksaScheduleSerializer, \
    DepartmentSerializer
from khumu.permissions import IsAuthenticatedKhuStudent, OpenPermission
from khumu.response import DefaultResponse

logger = logging.getLogger(__name__)

# 학과, 강의 같은 잡다한 검색 기능이 붙은 애들의 pagination
from user.models import KhumuUser

class KhuDomainSearchPagination(pagination.PageNumberPagination):

    page_size = 15  # 임의로 설정하느라 우선 크게 잡았음.
    page_query_param = 'page'
    page_size_query_param = 'size'
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })

class OrganizationListView(generics.ListAPIView):

    pagination_class = KhuDomainSearchPagination
    serializer_class = OrganizationSerializer
    permission_classes = [OpenPermission]

    def get_queryset(self):
        # 강의 이름으로 검색
        query_name = self.request.query_params.get('query_name', None)

        # 이름으로 검색.
        queryset = Organization.objects.filter(name__icontains=query_name) if query_name \
            else Organization.objects.all()

        return queryset

class DepartmentListView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [OpenPermission]

    def get_queryset(self):
        # 강의 이름으로 검색
        return Department.objects.all()

class LectureSuiteListView(generics.ListAPIView):

    pagination_class = KhuDomainSearchPagination
    serializer_class = LectureSuiteSerializer
    permission_classes = [OpenPermission]

    def get_queryset(self):
        # 강의 이름으로 검색
        query_name = self.request.query_params.get('query_name', None)
        # 단과대 Id로 검색
        query_organization_id = self.request.query_params.get('query_organization_id', None)

        # 우선 단과대로 검색.
        queryset = LectureSuite.objects.filter(department__organization__id=query_organization_id) if query_organization_id \
            else LectureSuite.objects.all()
        queryset = queryset.filter(name__icontains=query_name) if query_name \
            else queryset

        return queryset

class HaksaScheduleViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = HaksaScheduleSerializer
    permission_classes = [OpenPermission]

    # 최근 5개의 학사일정을 가져옵니다.
    def get_queryset(self):
        # 빨리 시작하는 순으로 5개 정렬
        # 표기상으로는 UTC+9라서 9시간 느리게 표기됨.
        confirmed = self.request.query_params.get('confirmed')
        if confirmed == 'true':
            return HaksaSchedule.objects.filter(ends_at__gte=timezone.now(), confirmhaksaschedule__in=ConfirmHaksaSchedule.objects.filter(user=self.request.user)).order_by(
                'starts_at')[:8]
        elif confirmed == 'false':
            return HaksaSchedule.objects.filter(ends_at__gte=timezone.now()).exclude(confirmhaksaschedule__in=ConfirmHaksaSchedule.objects.filter(user=self.request.user)).order_by(
                'starts_at')[:8]

        return HaksaSchedule.objects.filter(ends_at__gte=timezone.now()).order_by('starts_at')[:8]

    @action(methods=['POST'], detail=True, url_path='confirm')
    def confirm(self, request, pk):
        logger.info(f'{pk}를 읽음 처리합니다.')
        confirm = ConfirmHaksaSchedule(user=request.user, haksa_schedule_id=pk)
        confirm.save()

        return DefaultResponse(None, f'학사일정({pk})을 읽었습니다.', 200)

    @action(methods=['POST'], detail=False, url_path='notify')
    def notify(self, request):
        starts_at_min = timezone.now()
        starts_at_max = starts_at_min + timezone.timedelta(days=2)
        logger.info(f'현재 시각 {starts_at_min}')
        schedules = HaksaSchedule.objects.filter(is_notified=False, starts_at__gte=starts_at_min, starts_at__lte=starts_at_max)
        serializer = self.get_serializer(instance=schedules, many=True)

        for instance in serializer.instance:
            instance.is_notified = True
            instance.save()
            adapter.slack.slack.send_message('새로운 학사일정 임박', instance.title)
            if settings.SNS['enabled']:
                adapter.message.publisher.publish("haksa_schedule", "start", instance)

        return DefaultResponse(data=serializer.data, message=None, status=200)

class KhuSyncAPIView(APIView):

    def post(self, request):
        info21_id = request.data['id']
        info21_password = request.data['password']
        # 강의 동기화 작업
        job = KhuLectureSyncJob({
            "id": info21_id,
            "password": info21_password,
        })
        try:
            job.process()
        except Exception as e:
            traceback.print_exc()
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(e)})
        return Response(status=status.HTTP_200_OK, data={
            'message': '수강 중인 강의들의 게시판을 팔로우했습니다.'
        })