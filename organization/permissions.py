from rest_framework.permissions import BasePermission

class IsOrganization(BasePermission):
    """
    Allows access only to organzations
    """

    def has_permission(self, request, view):

        allow = bool(
            request.user and request.user.is_authenticated and request.user.is_organization
        )
        if not allow:
            self.message = {"error": "You are not an organization user"}
        return allow