from typing import Any

from django.test.client import RequestFactory
import pytest

from djapm.apm.contrib import _contribute_to_request
from djapm.apm.types import ApmRequest, PatchedHttpRequest

from tests.types import ApmRequestFactory


@pytest.fixture
def apm_rf(rf: RequestFactory, admin_user) -> ApmRequestFactory:
    """Request factory for a APM view, that calls `_contribute_to_request`"""

    def wrapper(
        method: str, url: str, view: Any, drf_req: bool = False, user=None
    ) -> PatchedHttpRequest:
        func = getattr(rf, method.lower())
        req = func(url)
        req.user = user or admin_user

        rest_req = None
        if drf_req:
            rest_req = ApmRequest(req)

        _contribute_to_request(req, view=view, logger_name=None, rest_request=rest_req)
        return req

    return wrapper
