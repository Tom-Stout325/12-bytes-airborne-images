from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import pwa_home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),    
    path('finance/', include('finance.urls')),
    path('drones/', include('drones.urls')),
    path('', pwa_home_redirect),  # PWA users land here first
]

if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



