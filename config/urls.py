from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.defaults import page_not_found, server_error
from oauth2_provider import urls as oauth2_urls


def page_not_found_view(request):
    return page_not_found(request, None)


urlpatterns = [
    path("", include("app.urls")),
    path("", include("users.urls")),
    path("datasets/", include("datasets.urls", namespace="datasets")),
    path("select2/", include("django_select2.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("o/", include(oauth2_urls)),
    path("404/", page_not_found_view, name="404"),
    path("500/", server_error, name="500"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
