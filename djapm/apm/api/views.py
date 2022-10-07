from datetime import timedelta
from django.db.models import Count, F, Avg, Max, Min
from django.db.models.functions import Extract, TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from djapm.apm import models


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def req_count_by_date(request: Request):
    result = (
        models.ApiRequest.objects.select_related("error_trace")
        .filter(requested_at__date__gte=timezone.now() - timedelta(days=7))
        .annotate(date=TruncDate("requested_at"))
        .values("date")
        .annotate(count=Count("id"), errors=Count("error_trace"))
        .order_by("date")
        .values("date", "count", "errors")
    )
    datasets = {
        "requests": {str(r["date"]): r["count"] for r in result},
        "errors": {str(r["date"]): r["errors"] for r in result},
    }
    return Response(datasets)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def req_view_name_count_by_date(request: Request):
    result = (
        models.ApiRequest.objects.select_related("error_trace")
        .filter(requested_at__date__gte=timezone.now())
        .values("view_name")
        .annotate(count=Count("id"), errors=Count("error_trace"))
        .order_by("view_name")
        .values("view_name", "count", "errors")
    )
    datasets = {
        "requests": {r["view_name"]: r["count"] for r in result},
        "errors": {r["view_name"]: r["errors"] for r in result},
    }
    return Response(datasets)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def response_view_name_ellapsed_time(request: Request):
    result = (
        models.ApiResponse.objects.select_related("request")
        .filter(request__requested_at__date__gte=timezone.now() - timedelta(days=7))
        .annotate(view_name=F("request__view_name"))
        .values("view_name")
        .order_by("view_name")
        .annotate(
            avg_ellapsed=Avg("ellapsed"),
            max_ellapsed=Max("ellapsed"),
            min_ellapsed=Min("ellapsed"),
        )
        .values("view_name", "avg_ellapsed", "max_ellapsed", "min_ellapsed")
    )
    datasets = {
        "avg": {r["view_name"]: r["avg_ellapsed"] for r in result},
        "max": {r["view_name"]: r["max_ellapsed"] for r in result},
        "min": {r["view_name"]: r["min_ellapsed"] for r in result},
    }
    return Response(datasets)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def response_ellapsed_time_by_date(request: Request):
    result = (
        models.ApiResponse.objects.select_related("request")
        .filter(request__requested_at__date__gte=timezone.now() - timedelta(days=7))
        .annotate(date=TruncDate("request__requested_at"))
        .values("date")
        .order_by("date")
        .annotate(
            avg_ellapsed=Avg("ellapsed"),
            max_ellapsed=Max("ellapsed"),
            min_ellapsed=Min("ellapsed"),
        )
        .values("date", "avg_ellapsed", "max_ellapsed", "min_ellapsed")
    )
    datasets = {
        "avg": {str(r["date"]): r["avg_ellapsed"] for r in result},
        "max": {str(r["date"]): r["max_ellapsed"] for r in result},
        "min": {str(r["date"]): r["min_ellapsed"] for r in result},
    }
    return Response(datasets)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def requests_count_by_hour(request: Request):
    now = timezone.now()
    yesterday = now - timedelta(hours=23)
    result = (
        models.ApiRequest.objects.filter(requested_at__gte=yesterday)
        .annotate(hour=Extract("requested_at", "hour"))
        .values("hour")
        .annotate(count=Count("id"))
        .values_list("hour", "count")
    )
    # Format the date as string so chartjs does not sort
    hourfmt = lambda n: f"{str(n).zfill(2)}:00"
    output = {}  # create a new map so results keep the order that was inserted
    result = dict(result)
    for hour in range(yesterday.hour, 24):
        output[hourfmt(hour)] = result.get(hour, 0)
    for hour in range(0, now.hour + 1):
        output[hourfmt(hour)] = result.get(hour, 0)

    return Response(output)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def errors_per_exception_class(request: Request):
    result = (
        models.ErrorTrace.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        .values("exception_class")
        .annotate(count=Count("request_id"))
        .values_list("exception_class", "count")
    )
    return Response(dict(result))
