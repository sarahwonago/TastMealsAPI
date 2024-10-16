from django.urls import path

from .views import (
                    RedemptionOptionDetailView,RedemptionOptionListCreateView,RedemptionTransactionDetailView, RedemptionTransactionListView, MarkRedemptionTransactionDeliveredView
                   )


urlpatterns = [

    # redemption option endpoints
    path('', RedemptionOptionListCreateView.as_view(), name='redemption-options'),
    path('<uuid:pk>/', RedemptionOptionDetailView.as_view(), name='redemption-option-detail'),

    # redemption option transaction endpoints
    path('redeem/transactions/', RedemptionTransactionListView.as_view(), name='redemption-transactions'),
    path('redeem/transactions/<uuid:pk>/', RedemptionTransactionDetailView.as_view(), name='redemption-transaction-detail'),
    path('redeem/transactions/<uuid:pk>/mark-delivered/', MarkRedemptionTransactionDeliveredView.as_view(), name='redemption-transaction-delivered'),

]

