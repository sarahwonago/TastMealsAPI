from django.urls import path

from .views import CustomerHomeAPIView


urlpatterns = [
    path("", CustomerHomeAPIView.as_view(), name="customer-home"),
 
]
