from django.contrib.admin.sites import site
from django.urls import path

from djapm.apm import views
from djapm.apm.api import views as api_views


urlpatterns = [
    path(
        "dashboard/",
        site.admin_view(views.render_dashboard),
        name="apm-dashboard",
    ),
    path(
        "metrics/rc_date/",
        api_views.req_count_by_date,
        name="request_count_by_date",
    ),
    path(
        "metrics/rvnc_date/",
        api_views.req_view_name_count_by_date,
        name="request_view_name_count_by_date",
    ),
    path(
        "metrics/rvne_date/",
        api_views.response_view_name_ellapsed_time,
        name="response_view_name_ellapsed_time",
    ),
    path(
        "metrics/ret_date/",
        api_views.response_ellapsed_time_by_date,
        name="response_ellapsed_time_by_date",
    ),
    path(
        "metrics/rch/",
        api_views.requests_count_by_hour,
        name="requests_count_by_hour",
    ),
    path(
        "metrics/epec/",
        api_views.errors_per_exception_class,
        name="errors_per_exception_class",
    ),
]
