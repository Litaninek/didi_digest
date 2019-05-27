from rest_framework.permissions import BasePermission
from rest_framework import permissions

CREATE_UPDATE_DELETE_METHODS = ('POST', 'PATCH', 'PUT', 'DELETE')


class IsAdminOrReadOnly(BasePermission):
    """
    Allows access for authenticated users to read only and
    CRUD for admins.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        elif request.method in CREATE_UPDATE_DELETE_METHODS:
            return request.user and request.user.is_staff

        return False


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the object.
        return obj.user == request.user
