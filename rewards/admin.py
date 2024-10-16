from django.contrib import admin
from .models import RedemptionOption, RedemptionTransaction


admin.site.register(RedemptionOption)
admin.site.register(RedemptionTransaction)
