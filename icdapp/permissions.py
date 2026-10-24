from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Anyone may read (GET, HEAD, OPTIONS).
    Only authenticated staff users may create or delete records.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)
