"""Tables configuration for the Process Manager data display."""

from typing import ClassVar

import django_tables2 as tables
from django.utils.safestring import mark_safe

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\" "
    'class="btn btn-sm btn-primary text-white" title="View logs">LOGS</a>'
)


class ProcessTable(tables.Table):
    """Defines a Process Table for the data from the Process Manager."""

    uuid = tables.Column(
        verbose_name="UUID",
        attrs={
            "th": {"class": "header-style"},
            "td": {
                "class": "fw-bold text-break text-start",
                "style": "max-width: 400px; white-space: normal;",
            },
        },
    )
    name = tables.Column(
        verbose_name="Process Name",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {
                "class": "fw-bold text-primary text-center",
                "style": "white-space: nowrap;",
            },
        },
    )
    user = tables.Column(
        verbose_name="User",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {"class": "text-secondary text-center"},
        },
    )
    session = tables.Column(
        verbose_name="Session",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {"class": "text-secondary text-center"},
        },
    )
    status_code = tables.Column(
        verbose_name="Status",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {"class": "fw-bold text-center"},
        },
    )
    exit_code = tables.Column(
        verbose_name="Exit Code",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {"class": "text-center"},
        },
    )
    logs = tables.TemplateColumn(
        logs_column_template,
        verbose_name="Logs",
        attrs={
            "th": {"class": "header-style text-center"},
            "td": {"class": "text-center"},
        },
    )
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th": {"class": "header-style text-center"},
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "class": "form-check-input form-check-lg",
            },
            "td__input": {
                "class": "form-check-input form-check-lg text-center",
                "style": "transform: scale(1.5);",
            },
        },
    )

    class Meta:
        """Meta options for ProcessTable."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-striped table-hover table-responsive"
        }

    def render_status_code(self, value: str) -> str:
        """Render the status_code with softer, transparent backgrounds."""
        if value == "DEAD":
            return mark_safe(
                '<span class="badge dead-badge">DEAD</span>'
            )
        elif value == "RUNNING":
            return mark_safe(
                '<span class="badge running-badge">RUNNING</span>'
            )
        return mark_safe(
            f'<span class="badge bg-secondary rounded" style="font-size: 1.1rem;">{value}</span>'
        )

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            'hx-preserve="true" class="form-check-input form-check-lg row-checkbox" '
            'style="transform: scale(1.5);" _="on click set .row-checkbox.checked to my.checked">'
        )
