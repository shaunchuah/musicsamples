from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.defaults import page_not_found, server_error
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def page_not_found_view(request):
    return page_not_found(request, None)


urlpatterns = [
    path("", include("app.urls")),
    path("", include("users.urls")),
    path("datasets/", include("datasets.urls", namespace="datasets")),
    path("select2/", include("django_select2.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v3/schema/", SpectacularAPIView.as_view(), name="api-v3-schema"),
    path(
        "api/v3/docs/",
        SpectacularSwaggerView.as_view(url_name="api-v3-schema"),
        name="api-v3-docs",
    ),
    path("admin/", admin.site.urls),
    path("404/", page_not_found_view, name="404"),
    path("500/", server_error, name="500"),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
