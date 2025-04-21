from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', lambda request: render(request, 'home.html'), name='home'),
    path('', include('app.urls')),
    path('', include('finance.urls')),
    path('', include('drone.urls')),
]

# Only serve media locally if not using S3
if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
