import requests
from typing import Any, Dict, List

from djapm.apm import models
from djapm.apm.integrations import base


__all__ = ("DiscordNotifier",)


class DiscordNotifier(base.Notificator):
    base_url = "https://discord.com/api"

    def __init__(
        self,
        integration: models.Integration,
        receivers: List[models.NotificationReceiver],
    ):
        self.oauth_token = integration.oauth_token
        self.receivers = receivers
        self.session = requests.session()
        self.session.headers.update({"Authorization": f"Bot {self.oauth_token}"})

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
        guilds_ids = self._get_guilds_ids()
        for guild_id in guilds_ids:
            for channel in self._get_guild_channels(guild_id):
                if channel["name"] == name:
                    return channel["id"]

        raise base.NotificationFailed(f"The channel {name} does not exists")

    def _get_guilds_ids(self) -> List[str]:
        response = self.session.get(self.base_url + "/users/@me/guilds")
        if not response.ok:
            raise base.NotificationFailed("Unable to retrieve guild ids")
        data = response.json()
        return [guild["id"] for guild in data]

    def _get_guild_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        response = self.session.get(self.base_url + f"/guilds/{guild_id}/channels")
        if not response.ok:
            raise base.NotificationFailed(
                f"Unable to retrieve the channels for {guild_id=}"
            )
        return response.json()

    def _send_notification(self, channel_id: str, message: str):
        DISCORD_MAX_CHARS_PER_MESSAGE = 2000
        response = self.session.post(
            self.base_url + f"/channels/{channel_id}/messages",
            json={"content": message[:DISCORD_MAX_CHARS_PER_MESSAGE]},
        )
        if not response.ok:
            raise base.NotificationFailed(
                f"Unable to send message to channel: {response.json()=}"
            )
