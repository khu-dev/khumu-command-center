from rest_framework import permissions
from django.contrib.auth.models import Group

from user.models import KhumuUser


class OpenPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return True

class IsAuthenticatedKhuStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.kind == 'student'


def is_author_or_admin(username:str, author:str):
    if KhumuUser.objects.get(username=username).groups.filter(name='admin'):
        return True
    else:
        return username == author