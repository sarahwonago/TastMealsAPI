from django.urls import path
from .views import RoleBasedRedirectAPIView

# if app grows namesapce the urls
#app_name = 'user_management'

urlpatterns = [
    path("role-based-redirect/", RoleBasedRedirectAPIView.as_view(), name="role-based-redirect"),
]
