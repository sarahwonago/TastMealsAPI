from django.urls import path

from .views import (
    AddReviewView, UpdateReviewView, UserReviewsView, DeleteReviewView, 
)


urlpatterns = [
  
    # endpoints for reviews
    path('orders/<uuid:order_id>/review/', AddReviewView.as_view(), name='customer-add-review'),
    path('reviews/', UserReviewsView.as_view(), name='customer-reviews'),
    path('reviews/<uuid:review_id>/update/', UpdateReviewView.as_view(), name='customer-update-review'),
    path('reviews/<uuid:review_id>/delete/', DeleteReviewView.as_view(), name='customer-delete-review'),

]
