from django.urls import path

from .views import CafeadminHomeAPIView


urlpatterns = [
    path("", CafeadminHomeAPIView.as_view(), name="cafeadmin-home"),
 
]
