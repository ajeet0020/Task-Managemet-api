from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access or modify it.
    Works for both Project (checking obj.owner) and Task (checking obj.project.owner).
    """

    def has_object_permission(self, request, view, obj):
        # Authenticated users only
        if not request.user or not request.user.is_authenticated:
            return False

        # If checking a Project instance
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        # If checking a Task instance
        if hasattr(obj, 'project'):
            return obj.project.owner == request.user

        return False

