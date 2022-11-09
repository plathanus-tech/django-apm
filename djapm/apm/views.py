from typing import Optional

from django.contrib.admin.sites import site
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View
from rest_framework.views import APIView

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


class ApmAPIView(APIView):
    """Apm Rest Framework class based view that will contribute to the incoming `request` before dispatching.
    Allowing it to be tracked by the middlewares."""

    logger_name: Optional[str] = None

    def dispatch(self, request, *args, **kwargs):
        rest_request = self.initialize_request(request, *args, **kwargs)
        contrib._contribute_to_request(
            request,
            view=self,
            logger_name=self.logger_name,
            rest_request=rest_request,
        )
        return super().dispatch(request, *args, **kwargs)


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
