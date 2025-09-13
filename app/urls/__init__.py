from django.urls import include, path

urlpatterns = [
    path("", include("app.urls.web")),
    path("", include("app.urls.samples")),
    path("", include("app.urls.datastore")),
    path("", include("app.urls.study_ids")),
    path("", include("app.urls.api")),
    path("", include("app.urls.api_v2")),
    path("boxes/", include("app.urls.boxes")),
]
