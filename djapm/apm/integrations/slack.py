import requests
from typing import List

from djapm.apm import models
from djapm.apm.integrations import base


__all__ = ("SlackNotifier",)


class SlackNotifier(base.Notificator):
    base_url = "https://slack.com/api"

    def __init__(
        self,
        integration: models.Integration,
        receivers: List[models.NotificationReceiver],
    ):
        self.oauth_token = integration.oauth_token
        self.receivers = receivers
        self.session = requests.session()
        self.session.headers.update({"Authorization": f"Bearer {self.oauth_token}"})

    def notify_error(self, message: str, trace: models.ErrorTrace):
        for receiver in self.receivers:
            if receiver.receiver_type == models.NotificationReceiver.ID_RECEIVER_TYPE:
                receiver_id = receiver.receiver
            elif (
                receiver.receiver_type == models.NotificationReceiver.NAME_RECEIVER_TYPE
            ):
                receiver_id = self._get_channel_id_by_name(receiver.receiver)
            else:
                continue
            self._send_notification(receiver_id, message)

    def _get_channel_id_by_name(self, name: str) -> str:
        response = self.session.get(self.base_url + "/conversations.list")
        data = response.json()
        if not data["ok"]:
            raise base.NotificationFailed(
                "Unable to retrieve the conversations/channels", response.text
            )
        for channel in data["channels"]:
            if channel["name"] == name:
                return channel["id"]
        raise base.NotificationFailed(
            f"The conversation/channel {name} does not exists"
        )

    def _send_notification(self, channel_id: str, message: str):
        response = self.session.post(
            self.base_url + "/chat.postMessage",
            json={"channel": channel_id, "text": message},
        )
        data = response.json()
        if not data["ok"]:
            raise base.NotificationFailed("Unable to send the message", response.text)
