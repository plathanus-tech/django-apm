from typing import Any, Protocol

from djapm.apm.types import PatchedHttpRequest


class ApmRequestFactory(Protocol):
    def __call__(
        self, method: str, url: str, view: Any, drf_req: bool = False, user=None
    ) -> PatchedHttpRequest:
        ...
