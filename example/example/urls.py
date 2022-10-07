from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("polls.urls")),
    path("apm/", include("djapm.apm.urls")),
]
