from rest_framework import permissions
from django.contrib.auth.models import Group
class OpenPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return True


def IsAuthorOrAdmin(username, author):
    return Group.objects.get(name="Admin").user_set.filter(username=username) or \
        username == author