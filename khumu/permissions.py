from rest_framework import permissions
from django.contrib.auth.models import Group


class OpenPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return True


def is_author_or_admin(username:str, author:str):
    return Group.objects.get(name="Admin").khumuuser_set.filter(username=username) or \
        username == author