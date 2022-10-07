from typing import Any, Dict, Optional

from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from djapm.apm import decorators, filters, models, types

__all__ = (
    "ApmModelAdmin",
    "ApiResponseInline",
    "ApiRequestAdmin",
    "ApiResponseAdmin",
    "RequestLogInline",
    "ErrorTraceAdmin",
    "NotificationReceiverInline",
    "IntegrationAdmin",
)


def span(value, style: str = ""):
    return f'<span style="{style}">{value}</span>'


def display_json(value: Optional[Dict[str, Any]]):
    if value is None:
        return "-"

    output = []
    output.append(span("{"))
    for k, v in value.items():
        if isinstance(v, (list, dict)):
            val = str(v)
        else:
            val = repr(v)
        output.append(
            span(repr(k), style="margin-left: 20px; color: grey;")
            + ": "
            + span(val, style="color: black;")
            + ","
        )
    output.append(span("}"))
    return mark_safe("<br>".join(output))


class ApmModelAdmin(admin.ModelAdmin):
    """A model admin that keep tracks of POST requests."""

    @decorators.apm_admin_view()
    def changeform_view(self, request: types.PatchedHttpRequest, *args, **kwargs):
        return super().changeform_view(request, *args, **kwargs)


class NoAddNoChangeMixin:
    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False


class ApiResponseInline(NoAddNoChangeMixin, admin.TabularInline):
    model = models.ApiResponse
    verbose_name = _("Response")
    readonly_fields = (
        "request",
        "status_code",
        "ellapsed",
        "created_at",
    )
    extra = 0

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(models.ApiRequest)
class ApiRequestAdmin(NoAddNoChangeMixin, admin.ModelAdmin):
    list_display = ("id", "user", "view_name", "method", "url", "requested_at")
    ordering = ("-requested_at",)
    readonly_fields = (
        "display_headers",
        "display_query_parameters",
        "query_string",
        "method",
        "url",
        "user",
        "view_name",
    )
    list_filter = ("method", "view_name")
    search_fields = ("id", "user")
    inlines = (ApiResponseInline,)
    fieldsets = (
        (_("Basic information"), {"fields": ("view_name", "method", "url", "user")}),
        (
            _("Headers"),
            {
                "fields": (
                    "display_headers",
                    "display_query_parameters",
                    "query_string",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("URL"))
    def url(self, obj: models.ApiRequest):
        if obj.query_string:
            return "?".join((obj.path, obj.query_string))
        return obj.path

    @admin.display(description=_("Headers"))
    def display_headers(self, obj: models.ApiRequest):
        return display_json(obj.headers)

    @admin.display(description=_("Query Parameters"))
    def display_query_parameters(self, obj: models.ApiRequest):
        return display_json(obj.query_parameters)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("response")


@admin.register(models.ApiResponse)
class ApiResponseAdmin(NoAddNoChangeMixin, admin.ModelAdmin):
    list_display = (
        "request_id",
        "request_method",
        "request_path",
        "requested_by",
        "status_code",
        "ellapsed",
        "created_at",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "request",
        "status_code",
        "ellapsed",
        "display_body",
        "created_at",
    )
    search_fields = ("request",)
    list_filter = ("status_code", filters.EllapsedTimeFilter)

    @admin.display(description=_("Body"))
    def display_body(self, obj: models.ApiResponse):
        return display_json(obj.body)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("request", "request__user")

    @admin.display(description=_("Method"))
    def request_method(self, obj: models.ApiResponse):
        return obj.request.method

    @admin.display(description=_("Path"))
    def request_path(self, obj: models.ApiResponse):
        return obj.request.path

    @admin.display(description=_("Requested By"))
    def requested_by(self, obj: models.ApiResponse):
        return obj.request.user


class RequestLogInline(NoAddNoChangeMixin, admin.TabularInline):
    model = models.RequestLog
    verbose_name = _("Log")
    verbose_name_plural = _("Logs")
    readonly_fields = (
        "timestamp",
        "level",
        "location",
        "message",
    )
    ordering = ("timestamp",)
    extra = 0

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False

    @admin.display(description=_("Location"))
    def location(self, obj: models.RequestLog):
        return f"{obj.file_path}:{obj.func_name}"


@admin.register(models.ErrorTrace)
class ErrorTraceAdmin(NoAddNoChangeMixin, admin.ModelAdmin):
    list_display = (
        "request_id",
        "exception_class",
        "exception_args",
        "created_at",
        "dismissed_at",
        "dismissed_by_user",
    )
    readonly_fields = (
        "request",
        "display_payload",
        "exception_class",
        "exception_args",
        "traceback",
        "created_at",
        "dismissed_at",
        "display_traceback",
        "dismissed_by_user",
    )
    search_fields = ("request", "exception_class")
    list_filter = ("created_at", "dismissed_at")
    fieldsets = (
        (_("Request"), {"fields": ("request", "display_payload")}),
        (
            _("Exception"),
            {
                "fields": ("exception_class", "exception_args", "display_traceback"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("created_at", "dismissed_at", "dismissed_by_user")},
        ),
    )
    ordering = ("dismissed_at", "-created_at")
    inlines = (RequestLogInline,)
    actions = ("dismiss_traces",)

    @admin.display(description=_("Traceback"))
    def display_traceback(self, obj: models.ErrorTrace):
        lines = iter(obj.traceback.splitlines())
        offset = 20
        display = []
        display.append(next(lines))
        for i, line in enumerate(lines):
            is_even = i % 2
            line_offset = offset * (is_even + 1)
            display.append(
                f'<span style="margin-left: {line_offset}px; color:{"grey" if not is_even else "black"};">{line}</span>'
            )
        return mark_safe("<br>".join(display))

    @admin.display(description=_("Payload"))
    def display_payload(self, obj: models.ErrorTrace):
        return display_json(obj.payload)

    @admin.action(description=_("Dismiss selected Error Traces"))
    def dismiss_traces(self, request, queryset):
        updated = queryset.filter(dismissed_at__isnull=True).update(
            dismissed_at=timezone.now(), dismissed_by_user=request.user
        )
        self.message_user(request, _("%s Errors dismissed") % updated, "INFO")


class NotificationReceiverInline(admin.TabularInline):
    model = models.NotificationReceiver
    fields = ("integration", "receiver_type", "receiver")
    extra = 3


@admin.register(models.Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ("platform", "created_by_user")
    fields = ("platform", "oauth_token")
    inlines = (NotificationReceiverInline,)

    def get_readonly_fields(self, request, obj: Optional[models.Integration] = None):
        if obj is None:
            return ("created_by_user",)
        return ("oauth_token", "created_by_user")

    def get_fieldsets(self, request, obj: Optional[models.Integration] = None):
        if obj is None or obj.created_by_user != request.user:
            return super().get_fieldsets(request, obj)
        return (
            (None, {"fields": ("platform", "created_by_user")}),
            (_("Credentials"), {"fields": ("oauth_token",), "classes": ("collapse",)}),
        )

    def save_model(
        self,
        request,
        obj: models.Integration,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        if not change:
            obj.created_by_user = request.user
        return super().save_model(request, obj, form, change)
