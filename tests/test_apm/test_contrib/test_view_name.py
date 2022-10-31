import pytest

from django.test.client import RequestFactory
from django.urls import reverse
from rest_framework.request import Request

from djapm.apm.contrib import _contribute_to_request
from polls.views import OrderedPolls, get_polls_page, get_polls


def test_contribute_to_request_on_regular_class_based_view(rf: RequestFactory):
    request = rf.get(reverse("polls-page-list-cbv"))
    _contribute_to_request(request, view=OrderedPolls.as_view(), logger_name=None)
    assert request.view_name == "polls.dj.OrderedPolls"


def test_contribute_to_request_on_regular_function_based_view(rf: RequestFactory):
    request = rf.get(reverse("polls-page-list"))
    _contribute_to_request(request, view=get_polls_page, logger_name=None)
    assert request.view_name == "polls.dj.get_polls_page"


@pytest.mark.xfail(reason="DRF CBV not yet implemented")
def test_contribute_to_request_on_drf_class_based_view():
    assert False


def test_contribute_to_request_on_drf_function_based_view(rf: RequestFactory):
    request = rf.get(reverse("polls-list"))
    _contribute_to_request(
        request, view=get_polls, logger_name=None, rest_request=Request(request)
    )
    assert request.view_name == "polls.drf.get_polls"
