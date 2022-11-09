from rest_framework import mixins, response

from djapm.apm import types


class ApmCreateModelMixin(mixins.CreateModelMixin):
    """A mixin that proxies the CreateModelMixin.
    Users that subclass this on the view get better type checking / hints.
    """

    def create(self, request: types.ApmRequest, *args, **kwargs) -> response.Response:
        return super().create(request, *args, **kwargs)


class ApmListModelMixin(mixins.ListModelMixin):
    """A mixin that proxies the ListModelMixin.
    Users that subclass this on the view get better type checking / hints.
    """

    def list(self, request: types.ApmRequest, *args, **kwargs) -> response.Response:
        return super().list(request, *args, **kwargs)


class ApmRetrieveModelMixin(mixins.RetrieveModelMixin):
    """A mixin that proxies the RetrieveModelMixin.
    Users that subclass this on the view get better type checking / hints.
    """

    def retrieve(self, request: types.ApmRequest, *args, **kwargs) -> response.Response:
        return super().retrieve(request, *args, **kwargs)


class ApmUpdateModelMixin(mixins.UpdateModelMixin):
    """A mixin that proxies the UpdateModelMixin.
    Users that subclass this on the view get better type checking / hints.
    """

    def update(self, request: types.ApmRequest, *args, **kwargs) -> response.Response:
        return super().update(request, *args, **kwargs)


class ApmDestroyModelMixin(mixins.DestroyModelMixin):
    """A mixin that proxies the DestroyModelMixin.
    Users that subclass this on the view get better type checking / hints.
    """

    def destroy(self, request: types.ApmRequest, *args, **kwargs) -> response.Response:
        return super().destroy(request, *args, **kwargs)
