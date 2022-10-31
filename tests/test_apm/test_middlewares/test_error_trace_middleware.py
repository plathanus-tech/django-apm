import warnings

from django.urls import reverse

from djapm.apm.middlewares import ErrorTraceMiddleware
from polls.views import get_polls
from tests.types import ApmRequestFactory


def test_process_exception_warns_when_debug_true_and_notify_on_debug_true_is_false(
    settings, apm_rf: ApmRequestFactory
):
    settings.DEBUG = True
    settings.APM_NOTIFY_ON_DEBUG_TRUE = False

    middleware = ErrorTraceMiddleware(lambda r: r)

    with warnings.catch_warnings(record=True) as w:
        request = apm_rf("GET", reverse("polls-list"), get_polls, drf_req=True)
        middleware.process_exception(request, ValueError("Oops, A exception occurred"))

        assert len(w) == 1, "No warnings were emitted"
