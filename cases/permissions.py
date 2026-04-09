from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    """
    صلاحية مخصصة للسماح فقط للمستخدمين الذين لديهم دور 'doctor'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'doctor'
