from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies.views import admin_dashboard

urlpatterns = [
    # Custom admin dashboard (must come before admin.site.urls to take precedence)
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    # Django admin panel
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('users.urls')),
    path('movies/', include('movies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
