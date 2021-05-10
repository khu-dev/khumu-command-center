from rest_framework import viewsets, pagination, permissions, views, status
from rest_framework import response

from khu_domain.models import LectureSuite, Organization
from khu_domain.serializers import LectureSuiteSerializer, OrganizationSerializer
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
