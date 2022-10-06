from datetime import datetime
import logging
from time import perf_counter
import traceback

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response

from djapm.apm import types, models, dflt_conf, tasks


__all__ = (
    "ApiMetricsMiddleware",
    "ErrorTraceMiddleware",
)


def api_request_defaults(req: types.PatchedHttpRequest):
    save_headers = getattr(
        settings,
        "APM_REQUEST_SAVE_HEADERS",
        dflt_conf.APM_REQUEST_SAVE_HEADERS,
    )
    save_qp = getattr(
        settings,
        "APM_REQUEST_SAVE_QUERY_PARAMETERS",
        dflt_conf.APM_REQUEST_SAVE_QUERY_PARAMETERS,
    )
    save_qs = getattr(
        settings,
        "APM_REQUEST_SAVE_QUERY_STRING",
        dflt_conf.APM_REQUEST_SAVE_QUERY_STRING,
    )
    return {
        "headers": dict(req.headers) if save_headers else None,
        "query_parameters": req.GET if save_qp else None,
        "query_string": req.META.get("QUERY_STRING") if save_qs else None,
        "view_name": req.view_name,
        "method": req.method,
        "path": req.path,
        "user_id": getattr(req.user, "id", None),
    }


def api_response_defaults(res: Response, ellapsed: float):
    return {
        "status_code": res.status_code,
        "ellapsed": ellapsed,
        "body": getattr(res, "data", None) if res.status_code >= 400 else None,
    }


class ApiMetricsMiddleware:
    """A middleware that will register a Request/Response associated data"""

    def __init__(self, get_response: types.GetResponse):
        self.get_response = get_response

    def __call__(self, request: types.PatchedHttpRequest):
        request.started_at = perf_counter()
        response = self.get_response(request)
        ellapsed = perf_counter() - request.started_at
        if not hasattr(request, "id"):
            # This request was not processed by the decorator `apm_api_view`
            return response
        self._register_metric(request, response, ellapsed)
        return response

    def process_exception(
        self, request: types.PatchedHttpRequest, exception: Exception
    ):
        if not hasattr(request, "id"):
            # This request was not processed by the decorator `apm_api_view`
            return
        # Due to the exception got raised, the ApiResponse was not created
        end = perf_counter()
        ellapsed = end - request.started_at
        models.ApiResponse.objects.create(
            request_id=request.id,
            status_code=500,
            ellapsed=ellapsed,
        )

    @staticmethod
    def _register_metric(
        request: types.PatchedHttpRequest, response: Response, ellapsed: float
    ):
        api_req, _ = models.ApiRequest.objects.get_or_create(
            defaults=api_request_defaults(request),
            id=request.id,
        )
        models.ApiResponse.objects.get_or_create(
            defaults=api_response_defaults(response, ellapsed),
            request=api_req,
        )


class ErrorTraceMiddleware:
    """A middleware that registers, and notifies Exceptions on views."""

    def __init__(self, get_response: types.GetResponse):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(
        self, request: types.PatchedHttpRequest, exception: Exception
    ):
        if not hasattr(request, "id"):
            # This request was not processed by the decorator `apm_api_view`
            return
        trace = self._register_error_trace(request, exception)
        use_celery = getattr(
            settings, "APM_NOTIFY_USING_CELERY", dflt_conf.APM_NOTIFY_USING_CELERY
        )
        if use_celery:
            tasks.send_notifications.apply_async(
                kwargs={"trace_id": trace.pk},
                countdown=3,
            )  # type: ignore
        else:
            tasks.send_notifications(trace_id=trace.pk)

    def _register_error_trace(
        self, request: types.PatchedHttpRequest, exception: Exception
    ) -> models.ErrorTrace:
        """Register a error trace for the current request/exception context"""
        models.ApiRequest.objects.get_or_create(
            defaults=api_request_defaults(request),
            id=request.id,
        )
        trace: models.ErrorTrace = models.ErrorTrace.objects.create(
            request_id=request.id,
            payload=request._json,
            exception_class=exception.__class__.__name__,
            exception_args=" ".join(exception.args),
            traceback=traceback.format_exc(),
        )
        models.RequestLog.objects.bulk_create(
            [
                models.RequestLog(
                    trace_id=trace.pk,
                    level=r.levelname,
                    file_path=r.pathname,
                    func_name=r.funcName,
                    timestamp=timezone.make_aware(datetime.fromtimestamp(r.created)),
                    message=r.getMessage(),
                )
                for r in request._log_handler.records
            ]
        )
        return trace
