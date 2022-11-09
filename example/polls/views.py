import random

from django.http import HttpResponse
from django.views.generic import ListView

from djapm.apm import decorators, generics
from djapm.apm.types import ApmRequest, PatchedHttpRequest
from djapm.apm.views import ApmView
from rest_framework import serializers
from rest_framework.response import Response

from polls.models import Poll


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = "__all__"


@decorators.apm_api_view(["GET"])
def get_polls(request: ApmRequest, **kwargs) -> Response:
    """A API-view that dont fails"""
    serializer = PollSerializer(Poll.objects.all(), many=True)
    return Response(serializer.data)


class Polls(generics.ApmListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class OrderedPolls(ApmView, ListView):
    # A view that will raise TemplateDoesNotExistsError
    queryset = Poll.objects.order_by("name")


@decorators.apm_api_view(["GET"])
def im_feeling_lucky(request: ApmRequest, **kwargs) -> Response:
    """A API-view that fails randomly"""
    request.logger.info(f"{request.user=} is feeling lucky")
    number = random.randint(0, 5)
    if number == 5:
        request.logger.error("The number of this time is not good")
        raise RecursionError("Oops, no luck this time")
    return Response({"message": "Your lucky bastard!"})


@decorators.apm_api_view(["GET", "POST"])
def fail(request: ApmRequest, **kwargs) -> Response:
    """A view that fails when posting"""
    if request.method == "POST":
        request.logger.info("Information")
        request.logger.warning("Warning")
        request.logger.error("Error")
        request.logger.critical("Critical")
        raise FileNotFoundError("Oops! failed")
    return Response()


@decorators.apm_view()
def get_polls_page(request: PatchedHttpRequest, **kwargs) -> HttpResponse:
    return HttpResponse()
