from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from accounts.views import CsrfInitView

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    # Wrap all API endpoints in 'api/' to match frontend
    path('api/', include([
        path('families/', include('families.urls')),
        path('auth/', include('accounts.urls')),
        path('news/', include('news.urls')),
        path('profiles/', include('profiles.urls')),
        path('csrf/', CsrfInitView.as_view()),
    ])),
    # Health check for Docker/Load balancer
    path('health/', health_check),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
