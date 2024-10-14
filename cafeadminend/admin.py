from django.contrib import admin
from .models import Notification, RedemptionOption, RedemptionTransaction

admin.site.register(Notification)
admin.site.register(RedemptionOption)
admin.site.register(RedemptionTransaction)
