from django.urls import path

from .views import (
    PaymentView
)


urlpatterns = [
   # make payment
   path("pay/<uuid:order_id>/", PaymentView.as_view(), name="customer-pay"),
]
