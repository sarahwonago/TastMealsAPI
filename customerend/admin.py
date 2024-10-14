from django.contrib import admin
from .models import  Payment, Review, CustomerLoyaltyPoint, Transaction

admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(CustomerLoyaltyPoint)
admin.site.register(Transaction)
