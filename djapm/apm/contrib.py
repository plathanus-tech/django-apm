import uuid
from typing import Any, Optional
from rest_framework.views import get_view_name

from djapm.apm import types, log


__all__ = ("_contribute_to_request",)


def _contribute_to_request(
    request: types.PatchedHttpRequest,
    *,
    view: Any,
    logger_name: Optional[str],
    rest_request: Optional[types.ApmRequest] = None,
):
    if rest_request is not None:
        data = rest_request.data
        view_name = get_view_name(view)
        if view_name == "Function":
            view_name = ".".join([view.__module__, getattr(view, "__name__", view.__class__.__name__)])
    else:
        data = request.POST
        view_name = ".".join([view.__module__, getattr(view, "__name__", view.__class__.__name__)])

    log._configure_logging(request=request, logger_name=logger_name)

    request.id = str(uuid.uuid4())
    request._json = data  # type: ignore
    request.view_name = view_name
