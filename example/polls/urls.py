from django.urls import path

from . import views


urlpatterns = [
    path("api/polls/", views.get_polls, name="polls-list"),
    path("api/polls/fail/", views.fail, name="polls-fail"),
]
