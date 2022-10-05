import logging

from celery import shared_task
from django.contrib.sites.models import Site
from django.urls import reverse

from djapm.apm import models
from djapm.apm.integrations import base


@shared_task(
    autoretry_for=(models.ErrorTrace.DoesNotExist,),
    max_retries=3,
)
def send_notifications(trace_id: str):
    trace = models.ErrorTrace.objects.get(pk=trace_id)
    integrations = models.Integration.objects.all()
    if not integrations:
        logging.critical("No integrations found! Error trace will not be notified")
        return
    for integration in integrations:
        Service = base.services.get(integration.platform)
        if not Service:
            logging.critical(f"No service found for {integration.platform=}")
            continue
        service = Service(integration, list(integration.receivers.all()))
        try:
            service.notify_error(get_error_message(trace), trace)
        except base.NotificationFailed as e:
            logging.critical(f"Failed to notify {integration.platform=} {e.args}")


def get_error_message(trace: models.ErrorTrace) -> str:
    """Returns the default message that is sent to the notificator"""
    request = trace.request
    admin_url = "https://%s%s" % (
        Site.objects.get_current().domain,
        reverse("admin:apm_errortrace_change", args=(trace.pk,)),
    )
    return """
Oops! A error ocurred.
Request ID: `{req_id}`
Checkout on admin: {admin_url}
URL: `{req_method} {req_path}`
Error: `{exc_class}: {exc_args}`
```{traceback}```
Logs associated with this request:
{logs}""".format(
        req_id=request.id,
        admin_url=admin_url,
        req_method=request.method,
        req_path=request.path,
        exc_class=trace.exception_class,
        exc_args=trace.exception_args,
        traceback="\n".join(trace.traceback.split("\n")[-10:]),
        logs="\n".join(
            [
                f"`[{l.timestamp!s} {l.level}] {l.message}`".format(l)
                for l in trace.logs.all()
            ]
        ),
    )
