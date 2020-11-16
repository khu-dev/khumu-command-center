from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework import response
from khumu.response import DefaultResponse
from user.serializers import KhumuUserSerializer, GroupSerializer
from user.models import KhumuUser

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