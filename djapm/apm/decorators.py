from functools import wraps
from typing import List, Optional

from rest_framework.decorators import api_view

from djapm.apm import contrib, types

__all__ = ("apm_api_view", "apm_view", "apm_admin_view")


def apm_api_view(allowed_methods: List[str], logger_name: Optional[str] = None):
    """Decorates a `rest_framework function-based view`.
    Upgrades the regular `request` (`rest_framework.request.Request`)
    parameter with an `ApmApiRequest` that contains more attributes (`id` `logger`).
    Applying this decorator allows the Apm middlewares to register/handle this request.
    It also apply the regular rest_framework's `api_view`,
    so there's no need to apply it on your view.

    Parameters:
    - `allowed_methods` `List[str]`: Which HTTP methods this view should handle,
    this value is passed directly to the rest_framework's `api_view` decorator.

    - `logger_name` `Optional[str]`: Optional logger_name that should be used to
    create the logger for this request.
    Defaults to the setting `APM_DEFAULT_LOGGER_NAME` if set, or fallbacks to `apm_api_view`.
    """

    def decorator(view: types.ApiApmView):
        @api_view(allowed_methods)
        @wraps(view)
        def inner(request: types.ApmRequest, *args, **kwargs):
            dj_request = request._request

            contrib._contribute_to_request(
                dj_request,
                view=view,
                logger_name=logger_name,
                rest_request=request,
            )
            return view(request, *args, **kwargs)

        return inner

    return decorator


def apm_view(logger_name: Optional[str] = None):
    """Decorates a `django function-based view`.
    Upgrades the regular `request` (django.http.HttpRequest) parameter
    with a `PatchedHttpRequest` that contains more attributes (`id`, `logger`).
    Applying this decorator allows the Apm middlewares to register/handle this request.

    Parameters:
    - `logger_name` `Optional[str]`: Optional logger_name that should be used to
    create the logger for this request.
    Defaults to the setting `APM_DEFAULT_LOGGER_NAME` if set, or fallbacks to `apm_api_view`.
    """

    def decorator(view: types.ApmView):
        @wraps(view)
        def inner(request: types.PatchedHttpRequest, *args, **kwargs):
            contrib._contribute_to_request(
                request,
                view=view,
                logger_name=logger_name,
            )
            return view(request, *args, **kwargs)

        return inner

    return decorator


def apm_admin_view(
    track_methods: Optional[List[str]] = None, logger_name: Optional[str] = None
):
    """Decorates a `django admin view`.
    Upgrades the regular `request` (django.http.HttpRequest) parameter
    with a `PatchedHttpRequest` that contains more attributes (`id`, `logger`).
    Applying this decorator allows the Apm middlewares to register/handle this request.

    Parameters:
    - `track_methods` `Optional[List[str]]`: Optional list of methods that should be tracked.
    Defaults to: ["POST"]
    - `logger_name` `Optional[str]`: Optional logger_name that should be used to
    create the logger for this request.
    Defaults to the setting `APM_DEFAULT_LOGGER_NAME` if set, or fallbacks to `apm_api_view`.
    """

    if track_methods is None:
        track_methods = ["POST"]

    def decorator(view):
        @wraps(view)
        def inner(self, request: types.PatchedHttpRequest, *args, **kwargs):

            if request.method in track_methods:
                contrib._contribute_to_request(
                    request,
                    view=view,
                    logger_name=logger_name,
                )
            return view(self, request, *args, **kwargs)

        return inner

    return decorator
