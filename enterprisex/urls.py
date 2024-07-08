from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),

    # Allauth URL's
    path('accounts/', include('allauth.urls')),
    
    path('', include('pages.urls', namespace='pages')),
    path('users/', include('users.urls', namespace='users')),
    path('payment/', include('payment.urls', namespace='payments')),
    
]

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("enterprisex.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]


# ERROR 404- NOT FOUND PAGE
#handler404 = 'shop.views.Erro404View'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
