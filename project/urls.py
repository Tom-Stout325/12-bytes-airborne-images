from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from app.views import test_session


from django.http import JsonResponse
def debug_csrf(request):
    return JsonResponse({
        'csrf_cookie': request.COOKIES.get('csrftoken', 'Not set'),
        'is_secure': request.is_secure(),
        'host': request.get_host(),
        'scheme': request.scheme,
        'x_forwarded_proto': request.META.get('HTTP_X_FORWARDED_PROTO'),
    })


urlpatterns = [
    path('debug-csrf/', debug_csrf, name='debug-csrf'),
    path('test-session/', test_session, name='test_session'),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('', include('finance.urls')),
    path('', include('drone.urls')),
]
# Only serve media locally if not using S3
if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
