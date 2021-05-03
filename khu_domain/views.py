from rest_framework import viewsets, pagination, permissions, views, status
from rest_framework import response

from khu_domain.models import LectureSuite
from khu_domain.serializers import LectureSuiteSerializer
from khumu.response import DefaultResponse


class LectureSuiteViewSet(viewsets.ModelViewSet):

    serializer_class = LectureSuiteSerializer

    def get_queryset(self):
        # 강의 이름으로 검색
        query_name = self.request.query_params.get('query_name', None)
        # 교수 이름으로 검색
        query_professor = self.request.query_params.get('query_professor', None)
        # 단과대 Id로 검색
        query_organization = self.request.query_params.get('query_organization', None)

        # 우선 단과대로 검색.
        queryset = LectureSuite.objects.filter(department__organization__id=query_organization) if query_organization \
            else LectureSuite.objects.all()
        queryset = queryset.filter(name__search=query_name) if query_name \
            else queryset
        queryset = queryset.filter(professor__search=query_professor) if query_professor \
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
    #
    # def retrieve(self, request, *args, **kwargs):
    #     article = self.get_object()
    #     article_serialized = self.get_serializer(article).data
    #
    #     return DefaultResponse(article_serialized)