from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authentication.urls")),
    path("", include("app.urls")),
    path("uploads/", include("ckeditor_uploader.urls")),
    path("select2/", include("django_select2.urls")),
    path("api-auth/", include("rest_framework.urls")),
    # path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
