from typing import Dict, List, Protocol, Type

from djapm.apm import models


__all__ = ("NotificationFailed", "Notificator", "services")


class NotificationFailed(Exception):
    pass


class Notificator(Protocol):
    """A Notificator is a class that knows how to
    send a notification to a specific integration.
    Notificator are registered on the `services` variable
    at the module level on `djapm.apm.integration.base` at runtime.
    """

    def __init__(
        self,
        integration: models.Integration,
        receivers: List[models.NotificationReceiver],
    ):
        """The notificator receives the `integration` and
        `receivers` that should send the notification.
        The `integration` may contain all the required data
        to authenticate this notificator with the external service.
        """
        ...

    def notify_error(self, message: str, trace: models.ErrorTrace) -> None:
        """Notify the `receivers` with the received default `message`
        provided by the middleware, or create your own using the
        `trace` object. Raise `NotificationFailed` if the service
        was unable to deliver the notification.
        """
        ...


services: Dict[str, Type[Notificator]] = {}
