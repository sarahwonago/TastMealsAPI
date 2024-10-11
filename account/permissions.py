from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Custom permission to allow only users with the role 'cafeadmin'
    to access admin endpoints.
    """

    message = "You are not permitted to access this endpoint."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'cafeadmin'
    
class IsCustomer(BasePermission):
    """
    Custom permission to allow only users with the role 'customer'
    to access customer endpoints.
    """
    
    message = "You are not permitted to access this endpoint."

    def has_permission(self, request, view):
         return request.user.is_authenticated and request.user.role == 'customer'
    
