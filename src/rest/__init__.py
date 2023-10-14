from rest_framework import permissions, viewsets


class IsAdminGroupUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name="admin").exists()


class ViewForAdmins(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser, IsAdminGroupUser]
