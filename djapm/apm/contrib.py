import uuid
from typing import Optional

from djapm.apm import types, log

__all__ = ("_contribute_to_request",)


def _contribute_to_request(
    request: types.PatchedHttpRequest,
    *,
    logger_name: Optional[str],
    rest_request: Optional[types.ApmRequest] = None,
):
    if rest_request is not None:
        data = rest_request.data
    else:
        data = request.POST

    log._configure_logging(request=request, logger_name=logger_name)

    request.id = str(uuid.uuid4())
    request._json = data  # type: ignore
