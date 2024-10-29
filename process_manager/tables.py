import django_tables2 as tables
from django.utils.safestring import mark_safe

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
        attrs={
            "th": {
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;"
            },
            "td": {
                "class": "fw-bold text-break text-start",
                "style": "max-width: 400px; white-space: normal;",
            },
        },
    )
    name = tables.Column(
        verbose_name="Process Name",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {
                "class": "fw-bold text-primary text-center",
                "style": "white-space: nowrap;",
            },
        },
    )
    user = tables.Column(
        verbose_name="User",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {"class": "text-secondary text-center"},
        },
    )
    session = tables.Column(
        verbose_name="Session",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {"class": "text-secondary text-center"},
        },
    )
    status_code = tables.Column(
        verbose_name="Status",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {"class": "fw-bold text-center"},
        },
    )
    exit_code = tables.Column(
        verbose_name="Exit Code",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {"class": "text-center"},
        },
    )
    logs = tables.TemplateColumn(
        logs_column_template,
        verbose_name="Logs",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "td": {"class": "text-center"},
        },
    )
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th": {
                "class": "text-center",
                "style": "font-family: Arial, sans-serif; background-color: rgba(60, 60, 60, 0.8); font-weight: bold; font-size: 1.1rem; color: white;",
            },
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": header_checkbox_hyperscript,
                "class": "form-check-input form-check-lg",
            },
            "td__input": {
                "class": "form-check-input form-check-lg text-center",
                "style": "transform: scale(1.5);",
            },
        },
    )

    class Meta:
        orderable = False
        attrs = {
            "class": "table table-striped table-hover table-responsive",
            "style": "width: 100%;",  # Make the table occupy full width
        }

    def render_status_code(self, value: str) -> str:
        """Render the status_code with softer, transparent backgrounds."""
        if value == "DEAD":
            return mark_safe(
                '<span class="badge px-3 py-2 rounded" style="background-color: rgba(255, 0, 0, 0.1); color: #d9534f; font-size: 1.1rem;">DEAD</span>'
            )
        elif value == "RUNNING":
            return mark_safe(
                '<span class="badge px-3 py-2 rounded" style="background-color: rgba(0, 255, 0, 0.1); color: #5cb85c; font-size: 1.1rem;">RUNNING</span>'
            )
        return mark_safe(
            f'<span class="badge bg-secondary px-3 py-2 rounded" style="font-size: 1.1rem;">{value}</span>'
        )

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            f'hx-preserve="true" class="form-check-input form-check-lg row-checkbox" style="transform: scale(1.5);" _="{row_checkbox_hyperscript}">'
        )
