from django.contrib import admin

from polls import models


class VoteInline(admin.TabularInline):
    model = models.Vote
    fields = ("poll", "user")
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(models.Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    inlines = (VoteInline,)
