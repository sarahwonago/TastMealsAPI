from django.contrib import admin
from .models import Category, DiningTable, FoodItem, SpecialOffer, Notification

admin.site.register(Category)
admin.site.register(DiningTable)
admin.site.register(FoodItem)
admin.site.register(SpecialOffer)
admin.site.register(Notification)
