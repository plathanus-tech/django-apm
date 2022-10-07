from django.http import HttpResponse

from djapm.apm import decorators
from djapm.apm.types import ApmRequest, PatchedHttpRequest
from rest_framework import serializers
from rest_framework.response import Response

from polls.models import Poll


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = "__all__"


@decorators.apm_api_view(["GET"])
def get_polls(request: ApmRequest, **kwargs) -> Response:
    request.logger.warning("Trying to log")
    serializer = PollSerializer(Poll.objects.all(), many=True)
    return Response(serializer.data)


@decorators.apm_api_view(["GET", "POST"])
def fail(request: ApmRequest, **kwargs) -> Response:
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
