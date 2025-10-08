from django.urls import include, path

urlpatterns = [
    path("", include("app.urls.web")),
    path("", include("app.urls.samples")),
    path("datastore/", include("app.urls.datastore", namespace="datastore")),
    path("", include("app.urls.study_ids")),
    path("", include("app.urls.api")),
    path("", include("app.urls.api_v2")),
    path("", include("app.urls.api_v3")),
    path("boxes/", include("app.urls.boxes")),
]
