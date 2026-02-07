from django.contrib import admin
from django.urls import path, include
from accounts.views import CsrfInitView

urlpatterns = [
    path('admin/', admin.site.urls),
    # families API mounted at /api/families/
    path('api/families/', include('families.urls')),
    # accounts auth endpoints mounted at /api/auth/
    path('api/auth/', include('accounts.urls')),
    path('api/news/', include('news.urls')),
    path('api/profiles/', include('profiles.urls')),
    # CSRF init endpoint expected by frontend
    path('api/csrf/', CsrfInitView.as_view()),
]
