from django.urls import path

from . import views


urlpatterns = [
    path("polls/", views.get_polls_page, name="polls-page-list"),
    path("api/polls/", views.get_polls, name="polls-list"),
    path("api/polls/fail/", views.fail, name="polls-fail"),
    path("api/feeling_lucky/", views.im_feeling_lucky, name="feeling-lucky"),
]
