from django.urls import reverse

from polls.views import OrderedPolls, get_polls_page, get_polls, Polls
from tests.types import ApmRequestFactory


def test_contribute_to_request_on_regular_class_based_view(apm_rf: ApmRequestFactory):
    request = apm_rf("GET", reverse("polls-page-list-cbv"), OrderedPolls.as_view())
    assert request.view_name == "polls.dj.OrderedPolls"


def test_contribute_to_request_on_regular_function_based_view(
    apm_rf: ApmRequestFactory,
):
    request = apm_rf("GET", reverse("polls-page-list"), get_polls_page)
    assert request.view_name == "polls.dj.get_polls_page"


def test_contribute_to_request_on_drf_class_based_view(apm_rf: ApmRequestFactory):
    request = apm_rf("GET", reverse("polls-list-cbv"), Polls.as_view(), drf_req=True)
    assert request.view_name == "polls.drf.Polls"


def test_contribute_to_request_on_drf_function_based_view(apm_rf: ApmRequestFactory):
    request = apm_rf("GET", reverse("polls-list"), get_polls, drf_req=True)
    assert request.view_name == "polls.drf.get_polls"
