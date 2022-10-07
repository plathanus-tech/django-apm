from django.contrib import admin
from djapm.apm.admin import ApmModelAdmin

from polls import models


class VoteInline(admin.TabularInline):
    model = models.Vote
    fields = ("poll", "user")
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(models.Poll)
class PollAdmin(ApmModelAdmin):
    """An admin that keeps track of the model creations"""

    list_display = ("id", "name")
    inlines = (VoteInline,)
