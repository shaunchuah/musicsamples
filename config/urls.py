from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# import debug_toolbar

urlpatterns = [
    path("", include("app.urls")),
    path("", include("users.urls")),
    path("select2/", include("django_select2.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
