import traceback

from rest_framework import viewsets, pagination, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from job.khu_lecture_sync import KhuLectureSyncJob
from khu_domain.models import LectureSuite, Organization
from khu_domain.serializers import LectureSuiteSerializer, OrganizationSerializer
from khumu.permissions import IsAuthenticatedKhuStudent
from khumu.response import DefaultResponse

class OrganizationViewSet(viewsets.ModelViewSet):

    serializer_class = OrganizationSerializer

    def get_queryset(self):
        # 강의 이름으로 검색
        query_name = self.request.query_params.get('query_name', None)

        # 이름으로 검색.
        queryset = Organization.objects.filter(name__icontains=query_name) if query_name \
            else Organization.objects.all()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return DefaultResponse(serializer.data)

class LectureSuiteViewSet(viewsets.ModelViewSet):

    serializer_class = LectureSuiteSerializer

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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # serializer = self.get_serializer(queryset, many=True)
        # articles = serializer.data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return DefaultResponse(serializer.data)

class KhuSyncAPIView(APIView):
    permission_classes = [IsAuthenticatedKhuStudent]

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
            traceback.print_exception(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(e)})
        return Response(status=status.HTTP_200_OK, data={
            'message': '강의 목록을 수집했습니다.'
        })