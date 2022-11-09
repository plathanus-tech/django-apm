import uuid
from typing import Any, Optional, Tuple

from rest_framework.request import Request
from djapm.apm import types, log


__all__ = ("_contribute_to_request",)


def _contribute_to_request(
    request: types.PatchedHttpRequest,
    *,
    view: Any,
    logger_name: Optional[str],
    rest_request: Optional[Request] = None,
):
    data = request.POST
    prefix = "dj"
    if rest_request is not None:
        data = rest_request.data
        prefix = "drf"

    app, view_name = _app_view_name_from_view(view)

    log._configure_logging(request=request, logger_name=logger_name)

    request.id = str(uuid.uuid4())
    request._json = data  # type: ignore
    request.view_name = ".".join((app, prefix, view_name))


def _app_view_name_from_view(view: Any) -> Tuple[str, str]:
    app, *mod = view.__module__.split(".")

    view_name = getattr(view, "__name__", getattr(view.__class__, "__name__", "View"))
    if hasattr(view, "view_class"):
        view_name = view.view_class.__name__

    return app, view_name
