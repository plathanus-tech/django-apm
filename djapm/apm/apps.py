from django.apps import AppConfig


class ApmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djapm.apm"

    def ready(self) -> None:
        """Injects the Notifier's into the services when ready.
        Also import the tasks module."""
        from djapm.apm import tasks
        from djapm.apm.integrations import base, slack, discord
        from djapm.apm.models import Integration

        base.services[Integration.SLACK_PLATFORM] = slack.SlackNotifier
        base.services[Integration.DISCORD_PLATFORM] = discord.DiscordNotifier
