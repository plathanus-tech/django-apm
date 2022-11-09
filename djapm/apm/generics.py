from rest_framework import generics

from djapm.apm import mixins
from djapm.apm.views import ApmAPIView


class GenericApmAPIView(ApmAPIView, generics.GenericAPIView):
    """Base class for all other APM generic views."""


class ApmCreateAPIView(mixins.ApmCreateModelMixin, GenericApmAPIView):
    """The same from DRF's CreateAPIView with an extra that will be tracked by the APM middlewares"""

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ApmListAPIView(mixins.ApmListModelMixin, GenericApmAPIView):
    """The same from DRF's ListAPIView with an extra that will be tracked by the APM middlewares"""

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApmRetrieveAPIView(mixins.ApmRetrieveModelMixin, GenericApmAPIView):
    """The same from DRF's RetrieveAPIView with an extra that will be tracked by the APM middlewares"""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ApmDestroyAPIView(mixins.ApmDestroyModelMixin, GenericApmAPIView):
    """The same from DRF's DestroyAPIView with an extra that will be tracked by the APM middlewares"""

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ApmUpdateAPIView(mixins.ApmUpdateModelMixin, GenericApmAPIView):
    """The same from DRF's UpdateAPIView with an extra that will be tracked by the APM middlewares"""

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
