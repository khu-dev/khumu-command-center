from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework import permissions

from khumu.response import DefaultResponse
from user.serializers import KhumuUserSerializer, GroupSerializer
from user.models import KhumuUser

class KhumuUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = KhumuUser.objects.all().order_by('-created_at')
    serializer_class = KhumuUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return DefaultResponse(200, serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return DefaultResponse(200, self.get_object())

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
        return DefaultResponse(200, serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return DefaultResponse(200, self.get_object())