"""Defines the ProcessTable for displaying process data in a structured table format."""

import django_tables2 as tables
from django.utils.safestring import mark_safe
from typing import ClassVar

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\" "
    'class="btn btn-sm btn-primary text-white" title="View logs">LOGS</a>'
)

header_checkbox_hyperscript = "on click set .row-checkbox.checked to my.checked"
row_checkbox_hyperscript = """
on click
if <.row-checkbox:not(:checked)/> is empty
  set #header-checkbox.checked to true
else
  set #header-checkbox.checked to false
"""

class ProcessTable(tables.Table):
    """Defines a Process Table for the data from the Process Manager."""

    uuid = tables.Column(
        verbose_name="UUID",
        attrs={"td": {"class": "fw-bold text-break text-start"}},
    )
    name = tables.Column(
        verbose_name="Process Name",
        attrs={"td": {"class": "fw-bold text-primary text-center"}},
    )
    user = tables.Column(
        verbose_name="User",
        attrs={"td": {"class": "text-secondary text-center"}},
    )
    session = tables.Column(
        verbose_name="Session",
        attrs={"td": {"class": "text-secondary text-center"}},
    )
    status_code = tables.Column(
        verbose_name="Status",
        attrs={"td": {"class": "fw-bold text-center"}},
    )
    exit_code = tables.Column(
        verbose_name="Exit Code",
        attrs={"td": {"class": "text-center"}},
    )
    logs = tables.TemplateColumn(
        logs_column_template,
        verbose_name="Logs",
        attrs={"td": {"class": "text-center"}},
    )
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": header_checkbox_hyperscript,
                "class": "form-check-input form-check-input-lg",
            },
            "td__input": {
                "class": "form-check-input form-check-input-lg text-center",
            },
        },
    )

    class Meta:
        """Table meta options for rendering behavior and styling."""
        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-striped table-hover table-responsive",
        }

    def render_status_code(self, value: str) -> str:
        """Render the status_code with custom badge classes."""
        if value == "DEAD":
            return mark_safe('<span class="badge badge-dead">DEAD</span>')
        elif value == "RUNNING":
            return mark_safe('<span class="badge badge-running">RUNNING</span>')
        return mark_safe(
            f'<span class="badge bg-secondary px-3 py-2 rounded" style="font-size: 1.1rem;">{value}</span>'
        )

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            'hx-preserve="true" class="form-check-input form-check-input-lg row-checkbox" '
            f'_="{row_checkbox_hyperscript}">'
        )
