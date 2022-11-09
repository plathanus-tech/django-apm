from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from djapm.apm import dflt_conf

__all__ = (
    "ApiRequest",
    "ApiResponse",
    "ErrorTrace",
    "RequestLog",
    "Integration",
    "NotificationReceiver",
)


UserModel = get_user_model()


class ApmManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        database_alias = getattr(
            settings, "APM_USE_DATABASE", dflt_conf.APM_USE_DATABASE
        )
        return super().get_queryset().using(database_alias)


class ApmModel(models.Model):
    objects = ApmManager()

    class Meta:
        abstract = True


class ApiRequest(ApmModel):
    id = models.CharField(
        verbose_name=_("Request ID"),
        help_text=_("Unique identifier of this request"),
        max_length=36,
        primary_key=True,
        editable=False,
    )
    headers = models.JSONField(
        verbose_name=_("Request Headers"),
        help_text=_("The headers sent with this request"),
        editable=False,
        null=True,
    )
    query_parameters = models.JSONField(
        verbose_name=_("Request Query Parameters"),
        help_text=_("The query parameters sent with this request"),
        editable=False,
        null=True,
    )
    query_string = models.CharField(
        verbose_name=_("Query string"),
        help_text=_("The raw query parameter string sent with this request"),
        max_length=512,
        null=True,
        editable=False,
    )
    view_name = models.CharField(
        verbose_name=_("View name"),
        help_text=_("The name of the function/class that handled this request"),
        max_length=255,
        null=True,
        editable=False,
    )
    method = models.CharField(
        verbose_name=_("HTTP Method"),
        max_length=7,
        editable=False,
    )
    path = models.CharField(
        verbose_name=_("Path"),
        help_text=_("The request's URI"),
        max_length=256,
        editable=False,
    )
    user = models.ForeignKey(
        verbose_name=_("User"),
        help_text=_("The user associated with this request"),
        to=UserModel,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )
    requested_at = models.DateTimeField(
        verbose_name=_("Requested at"),
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = _("API Request")
        verbose_name_plural = _("API Requests")

    def __str__(self):
        return self.id


class ApiResponse(ApmModel):
    request = models.OneToOneField(
        verbose_name=_("Request"),
        to=ApiRequest,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="response",
        editable=False,
    )
    status_code = models.SmallIntegerField(
        verbose_name=_("Status code"),
        help_text=_("The response's status code"),
        editable=False,
    )
    ellapsed = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        verbose_name=_("Ellapsed"),
        help_text=_("How much time the server took to respond"),
        null=True,
        editable=False,
    )
    body = models.JSONField(
        verbose_name=_("Body"),
        help_text=_("The response's body"),
        null=True,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        auto_now_add=True,
        null=True,
        editable=False,
    )

    request_id: str

    class Meta:
        verbose_name = _("API Response")
        verbose_name_plural = _("API Responses")

    def __str__(self):
        return self.request_id


class ErrorTrace(ApmModel):
    request = models.OneToOneField(
        verbose_name=_("Request"),
        to=ApiRequest,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="error_trace",
        editable=False,
    )
    payload = models.JSONField(
        verbose_name=_("Request Payload"),
        help_text=_("The payload sent with this request"),
        null=True,
        editable=False,
    )
    exception_class = models.CharField(
        verbose_name=_("Exception class"),
        max_length=255,
        editable=False,
    )
    exception_args = models.CharField(
        verbose_name=_("Exception arguments"),
        max_length=255,
        editable=False,
    )
    traceback = models.TextField(
        verbose_name=_("Traceback"),
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        auto_now_add=True,
        editable=False,
    )
    dismissed_at = models.DateTimeField(
        verbose_name=_("Dismissed at"),
        null=True,
        editable=False,
    )
    dismissed_by_user = models.ForeignKey(
        verbose_name=_("Dismissed by user"),
        to=UserModel,
        on_delete=models.CASCADE,
        related_name="dismissed_traces",
        editable=False,
        null=True,
    )

    request_id: str
    logs: models.QuerySet["RequestLog"]

    class Meta:
        verbose_name = _("Error Trace")
        verbose_name_plural = _("Error Traces")

    def __str__(self):
        return self.request_id


class RequestLog(ApmModel):
    trace = models.ForeignKey(
        verbose_name=_("Error Trace"),
        to=ErrorTrace,
        on_delete=models.CASCADE,
        related_name="logs",
        editable=False,
    )
    level = models.CharField(
        verbose_name=_("Level"),
        max_length=10,
        editable=False,
    )
    file_path = models.CharField(
        verbose_name=_("File Path"),
        max_length=512,
        editable=False,
    )
    func_name = models.CharField(
        verbose_name=_("Function Name"),
        max_length=255,
        editable=False,
    )
    timestamp = models.DateTimeField(
        verbose_name=_("Time Stamp"),
        editable=False,
    )
    message = models.TextField(
        verbose_name=_("Message"),
        editable=False,
    )

    trace_id: str

    class Meta:
        verbose_name = _("Request Log")
        verbose_name_plural = _("Request Logs")

    def __str__(self):
        return self.trace_id


class Integration(ApmModel):
    SLACK_PLATFORM = "slack"
    DISCORD_PLATFORM = "discord"
    PLATFORMS = ((SLACK_PLATFORM, "Slack"), (DISCORD_PLATFORM, "Discord"))

    platform = models.CharField(
        verbose_name=_("Platform"),
        help_text=_("To which platform this integration refers"),
        max_length=50,
        unique=True,
        choices=PLATFORMS,
    )
    created_by_user = models.ForeignKey(
        verbose_name=_("Created by user"),
        to=UserModel,
        on_delete=models.CASCADE,
        related_name="created_integrations",
        editable=False,
    )
    oauth_token = models.CharField(
        verbose_name=_("OAuth Token"),
        max_length=255,
        null=True,
    )

    receivers: models.QuerySet["NotificationReceiver"]

    class Meta:
        verbose_name = _("Integration")
        verbose_name_plural = _("Integrations")

    def __str__(self):
        return self.platform


class NotificationReceiver(ApmModel):
    NAME_RECEIVER_TYPE = "name"
    ID_RECEIVER_TYPE = "id"

    RECEIVER_TYPES = (
        (NAME_RECEIVER_TYPE, _("Name")),
        (ID_RECEIVER_TYPE, _("ID")),
    )

    integration = models.ForeignKey(
        verbose_name=_("Integration"),
        to=Integration,
        on_delete=models.CASCADE,
        related_name="receivers",
    )
    receiver_type = models.CharField(
        verbose_name=_("Receiver Type"),
        max_length=50,
        choices=RECEIVER_TYPES,
    )
    receiver = models.CharField(
        verbose_name=_("Receiver"),
        help_text=_("Who should receive this message (Id/Name)"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Notification Receiver")
        verbose_name_plural = _("Notification Receivers")

    def __str__(self):
        return self.receiver
