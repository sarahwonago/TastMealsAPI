from django.contrib import admin
from .models import Cart, CartItem, Order, Payment

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Payment)
