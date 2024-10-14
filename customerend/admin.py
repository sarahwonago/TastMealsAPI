from django.contrib import admin
from .models import  Review, CustomerLoyaltyPoint, Transaction

admin.site.register(Review)
admin.site.register(CustomerLoyaltyPoint)
admin.site.register(Transaction)
