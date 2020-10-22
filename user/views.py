from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework import permissions
from user.serializers import KhumuUserSerializer, GroupSerializer
from user.models import KhumuUser

class KhumuUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = KhumuUser.objects.all().order_by('-date_joined')
    serializer_class = KhumuUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]