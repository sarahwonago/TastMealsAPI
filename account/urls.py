from django.urls import path

from .views import RoleBasedRedirectAPIView
urlpatterns = [
    path("role-based-redirect/", RoleBasedRedirectAPIView.as_view(), name="role-based-redirect"),
]