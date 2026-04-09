from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    """
    صلاحية مخصصة للسماح فقط للمستخدمين الذين لديهم دور 'doctor'.
    """
    def has_permission(self, request, view):
        # التأكد من أن المستخدم مسجل دخوله وأن دوره هو 'doctor'
        return request.user and request.user.is_authenticated and request.user.role == 'doctor'
