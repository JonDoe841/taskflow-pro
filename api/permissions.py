from rest_framework import permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class IsProjectMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            return obj.project.members.filter(id=request.user.id).exists()
        return False
class IsProjectManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Project Managers').exists()
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            return obj.project.projectmembership_set.filter(
                user=request.user,
                role__in=['owner', 'manager']
            ).exists()
        return False




