from typing import Optional

from django.contrib.admin.sites import site
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View

from djapm.apm import contrib, models, types


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
        contrib._contribute_to_request(request, view=self, logger_name=self.logger_name)
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


def render_dashboard(request):
    """Renders the dashboard in the admin"""
    return render(
        request,
        "apm/dashboard.html",
        {
            "opts": models.ApiRequest._meta,
            "is_nav_sidebar_enabled": True,
            "available_apps": site.get_app_list(request),
            "api_urls": {
                "RequestsCountByDate": reverse("request_count_by_date"),
                "RequestsViewNameCountToday": reverse(
                    "request_view_name_count_by_date"
                ),
                "ResponseEllapsedTimeByDate": reverse("response_ellapsed_time_by_date"),
                "ResponseEllapsedTimeByView": reverse(
                    "response_view_name_ellapsed_time"
                ),
                "RequestsCountLast24Hours": reverse("requests_count_by_hour"),
                "ErrorsPerClassLastWeek": reverse("errors_per_exception_class"),
            },
        },
    )
