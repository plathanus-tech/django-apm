from typing import Optional

from django.http import HttpResponse
from django.views.generic import View

from djapm.apm import contrib, types


__all__ = ("ApmView",)


class ApmView(View):
    """Apm Django Class-based view that will contribute to the `request` before dispatching.
    Allowing it to be tracked by the middlewares."""

    logger_name: Optional[str] = None

    def dispatch(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """Wraps the standard `View.dispatch`"""
        contrib._contribute_to_request(request, logger_name=self.logger_name)
        return super().dispatch(request, *args, **kwargs)

    # The methods defined below are for type-checking purposes only.
    # implementing them here, causes the same behavior if not implemented
    # (see super().dispatch()).

    def get(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def put(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def patch(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def delete(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def head(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def options(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)

    def trace(
        self,
        request: types.PatchedHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return self.http_method_not_allowed(request, *args, **kwargs)
