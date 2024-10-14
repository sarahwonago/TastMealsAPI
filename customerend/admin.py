from django.contrib import admin
from .models import Order, Payment, Review, CustomerLoyaltyPoint, Transaction

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(CustomerLoyaltyPoint)
admin.site.register(Transaction)
