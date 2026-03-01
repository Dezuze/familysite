from rest_framework.permissions import BasePermission


class IsGuardianOrSelf(BasePermission):
    """
    Permission that allows editing a FamilyMember profile if:
    - The request user IS the profile owner (profile.user_account == request.user)
    - OR the request user is the creator AND the profile is NOT independent
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods are always allowed for authenticated users
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # The profile owner always has full access
        if hasattr(obj, 'user_account') and obj.user_account == request.user:
            return True

        # Guardian: creator has write access only if profile is not independent
        if obj.created_by == request.user and not obj.is_independent:
            return True

        # Staff/superuser always has access
        if request.user.is_staff or request.user.is_superuser:
            return True

        return False
