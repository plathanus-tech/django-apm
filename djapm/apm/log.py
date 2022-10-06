import logging
from typing import List, Optional, TYPE_CHECKING

from django.conf import settings

from djapm.apm import dflt_conf


__all__ = ("ApmStreamHandler", "_configure_logging")


if TYPE_CHECKING:
    from djapm.apm.types import PatchedHttpRequest


class ApmStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records: List[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
        super().emit(record)


def _configure_logging(request: "PatchedHttpRequest", logger_name: Optional[str]):
    default_logger = getattr(
        settings, "APM_DEFAULT_LOGGER_NAME", dflt_conf.APM_DEFAULT_LOGGER_NAME
    )
    request.logger = logging.getLogger(logger_name or default_logger)
    request._log_handler = ApmStreamHandler()
    for handler in request.logger.handlers.copy():
        if isinstance(handler, ApmStreamHandler):
            request.logger.removeHandler(handler)
    request.logger.addHandler(request._log_handler)
