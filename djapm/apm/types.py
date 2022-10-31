import logging
from typing import Any, Callable, Dict, Protocol, Union
from django.http import HttpRequest, HttpResponse

from rest_framework.request import Request
from rest_framework.response import Response

from djapm.apm.log import ApmStreamHandler


__all__ = (
    "ApmRequest",
    "ApiApmView",
    "ApmView",
    "GetResponse",
    "PatchedHttpRequest",
)


class ApmRequest(Request):
    id: str
    view_name: str
    logger: logging.Logger
    _request: "PatchedHttpRequest"

    @property
    def user_id(self):
        user = self.user
        return getattr(user, "id", None)


class ApiApmView(Protocol):
    """A rest_framework-view that receives a ApmRequest and any kwargs"""

    def __call__(self, request: ApmRequest, *args, **kwargs) -> Response:
        ...


class ApmView(Protocol):
    """A regular django-view that receives a PatchedHttpRequest and any kwargs"""

    def __call__(self, request: "PatchedHttpRequest", *args, **kwargs) -> HttpResponse:
        ...


class GetResponse(Protocol):
    def __call__(self, request: Union[Request, HttpRequest]) -> Response:
        ...


class PatchedHttpRequest(HttpRequest):
    """An upgraded Django HttpRequest that contains some extra attributes."""

    id: str
    logger: logging.Logger
    view_name: str
    _log_handler: ApmStreamHandler
    started_at: float
    _json: Dict[str, Any]
