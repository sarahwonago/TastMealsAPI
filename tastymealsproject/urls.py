
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # builtin admin dashboard
    path("admin/", admin.site.urls),

    #djoser with simplejwt
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),

    path('api/customer/', include('customerend.urls')),
    path('api/cafeadmin/', include('cafeadminend.urls')),
    path("api/account/", include('account.urls')),
]

