from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    path("app/", TemplateView.as_view(template_name="index.html"), name="app"),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
]

# Serve media files in development
if settings.DEBUG and settings.USE_LOCAL_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
