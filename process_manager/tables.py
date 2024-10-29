"""Defines tables for displaying process data in the Process Manager application."""

from typing import ClassVar

import django_tables2 as tables
from django.utils.safestring import mark_safe

header_style = (
    "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); "
    "font-weight: bold; font-size: 1.1rem; color: white;"
)
status_dead_style = (
    "background-color: rgba(255, 0, 0, 0.1); color: #d9534f; font-size: 1.1rem;"
)
status_running_style = (
    "background-color: rgba(0, 255, 0, 0.1); color: #5cb85c; font-size: 1.1rem;"
)


class ProcessTable(tables.Table):
    """Defines a table structure for displaying process data with custom styles."""

    uuid = tables.Column(
        verbose_name="UUID",
        attrs={
            "th": {"style": header_style},
            "td": {"class": "fw-bold text-break text-start"},
        },
    )
    name = tables.Column(
        verbose_name="Process Name",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "fw-bold text-primary text-center"},
        },
    )
    user = tables.Column(
        verbose_name="User",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "text-secondary text-center"},
        },
    )
    session = tables.Column(
        verbose_name="Session",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "text-secondary text-center"},
        },
    )
    status_code = tables.Column(
        verbose_name="Status",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "fw-bold text-center"},
        },
    )
    exit_code = tables.Column(
        verbose_name="Exit Code",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "text-center"},
        },
    )
    logs = tables.TemplateColumn(
        "<a href=\"{% url 'process_manager:logs' record.uuid %}\" "
        'class="btn btn-sm btn-primary text-white" title="View logs">LOGS</a>',
        verbose_name="Logs",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "td": {"class": "text-center"},
        },
    )
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th": {"class": "text-center", "style": header_style},
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": "on click set .row-checkbox.checked to my.checked",
                "class": "form-check-input form-check-lg",
            },
            "td__input": {
                "class": "form-check-input form-check-lg text-center",
                "style": "transform: scale(1.5);",
            },
        },
    )

    class Meta:
        """Metadata options for configuring table behavior and appearance."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict] = {
            "class": "table table-striped table-hover table-responsive"
        }

    def render_status_code(self, value: str) -> str:
        """Render the status_code with softer, transparent backgrounds."""
        if value == "DEAD":
            return mark_safe(
                f'<span class="badge px-3 py-2 rounded" style="{status_dead_style}">'
                "DEAD</span>"
            )
        elif value == "RUNNING":
            return mark_safe(
                f'<span class="badge px-3 py-2 rounded" style="{status_running_style}">'
                "RUNNING</span>"
            )
        return mark_safe(
            f'<span class="badge bg-secondary px-3 py-2 rounded" '
            f'style="font-size: 1.1rem;">{value}</span>'
        )

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            'hx-preserve="true" class="form-check-input form-check-lg row-checkbox" '
            'style="transform: scale(1.5);" _="on click set .row-checkbox.checked to my.checked">'
        )
