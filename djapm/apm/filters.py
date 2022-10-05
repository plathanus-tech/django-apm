from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _


class EllapsedTimeFilter(admin.SimpleListFilter):
    title = _("Ellapsed Time")
    parameter_name = "ellapsed"

    def lookups(self, request, model_admin):
        self.available_lookups = (
            ("<=,0.2", _("Below 200ms")),
            (">=,0.2:<=,0.4", _("Between 200-400ms")),
            (">=,0.4:<=,0.6", _("Between 400-600ms")),
            (">=,0.6:<=,0.99", _("Between 600ms-1s")),
            (">=,1", _("Above 1s")),
        )
        return self.available_lookups

    def queryset(self, request, queryset: QuerySet):
        operators = {
            "<=": "lte",
            ">=": "gte",
        }
        value = self.value()
        if value is None or value not in [
            lookup for lookup, label in self.available_lookups
        ]:
            return queryset

        lookup_parts = value.split(":")
        for part in lookup_parts:
            lookup, filter_value = part.split(",")
            queryset = queryset.filter(
                **{f"{self.parameter_name}__{operators[lookup]}": float(filter_value)}
            )
        return queryset
