from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from accounts.views import CsrfInitView

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    # families API mounted at /families/
    path('families/', include('families.urls')),
    # accounts auth endpoints mounted at /auth/
    path('auth/', include('accounts.urls')),
    # news API mounted at /news/
    path('news/', include('news.urls')),
    # profiles API mounted at /profiles/
    path('profiles/', include('profiles.urls')),
    # CSRF init endpoint expected by frontend
    path('csrf/', CsrfInitView.as_view()),
    # Health check for Docker/Load balancer
    path('health/', health_check),
]
