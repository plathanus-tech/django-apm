from django.urls import path, include

from . import views


urlpatterns = [
    path("polls/", views.get_polls_page, name="polls-page-list"),
    path("api/polls/", views.get_polls, name="polls-list"),
    path("api/polls/fail/", views.fail, name="polls-fail"),
    path("apm/", include("djapm.apm.urls")),
]
