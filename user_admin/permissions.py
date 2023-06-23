from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allows access only to admins (not superusers)
    """

    def has_permission(self, request, view):

        allow = bool(
            request.user and request.user.is_authenticated and request.user.is_admin
        )
        if not allow:
            self.message = {"error": "You are not an admin"}
        return allow