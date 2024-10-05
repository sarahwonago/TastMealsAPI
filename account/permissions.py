from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Custom permission to allow only users with roles admin
    to access admin endpoints.
    """

    message = "You are not permitted to access this endpoint."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            print(request.user.role)

            return request.user.role == 'cafeadmin'
        return False
    
class IsCustomer(BasePermission):
    """
    Custom permission to allow only users with roles customer
    to access customer endpoints.
    """
    
    message = "You are not permitted to access this endpoint."

    def has_permission(self, request, view):
         if request.user.is_authenticated:
            print(request.user.role)
            return request.user.role == 'customer'
         return False