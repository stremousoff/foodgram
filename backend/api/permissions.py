from rest_framework import permissions


class OwnerAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET',):
            return True
        return obj.author == request.user or request.user.is_staff
