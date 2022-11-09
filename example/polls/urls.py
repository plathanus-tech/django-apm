from django.urls import path

from . import views


urlpatterns = [
    path("polls/", views.get_polls_page, name="polls-page-list"),
    path("polls-cbv/", views.OrderedPolls.as_view(), name="polls-page-list-cbv"),
    path("api/polls/", views.get_polls, name="polls-list"),
    path("api/polls-cbv/", views.Polls.as_view(), name="polls-list-cbv"),
    path("api/polls/fail/", views.fail, name="polls-fail"),
    path("api/feeling_lucky/", views.im_feeling_lucky, name="feeling-lucky"),
]
