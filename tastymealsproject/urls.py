
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # builtin admin panel
    path("admin/", admin.site.urls),

    #djoser with simplejwt
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),

    # api documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/schema/redoc/", SpectacularRedocView.as_view(url_name='schema'), name="redoc"),
    path("api/docs/schema/swagger/", SpectacularSwaggerView.as_view(url_name='schema'), name="swagger"),

    # endpoints
    path('api/customer/', include('customerend.urls')),
    path('api/cafeadmin/', include('cafeadminend.urls')),
    path("api/account/", include('account.urls')),
]

