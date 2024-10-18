from django.urls import path

from .views import DiningTableListAPIView, DiningTableDetailAPIView


urlpatterns = [
  
    # endpoint for managing dinning tables
    path("tables/", DiningTableListAPIView.as_view(), name="dinning-list-create"),
    path("tables/<uuid:pk>/", DiningTableDetailAPIView.as_view(), name="dinning-detail"),
]

