from rest_framework import permissions
from django.contrib.auth.models import Group


class OpenPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return True


def is_author_or_admin(username:str, author:str):
    admin_group = Group.objects.filter(name="Admin").first()
    if admin_group:
        return admin_group.khumuuser_set.filter(username=username) or \
        username == author
    else:
        return username == author