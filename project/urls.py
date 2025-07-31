from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import pwa_home_redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),    
    path('finance/', include('finance.urls')),
    path('drones/', include('drones.urls')),
    path('', pwa_home_redirect),
     path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/json')),
]

if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



