import django_tables2 as tables
from django.utils.safestring import mark_safe

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\" "
    "class=\"btn btn-sm btn-primary text-white\" title=\"View logs\">LOGS</a>"
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

    uuid = tables.Column(verbose_name="UUID", attrs={
        "td": {"class": "fw-bold text-break", "style": "max-width: 300px; white-space: normal;"}
    })  # Increased max-width for UUID to make it wider
    name = tables.Column(verbose_name="Name", attrs={
        "td": {"class": "fw-bold text-primary", "style": "white-space: nowrap;"}
    })
    user = tables.Column(verbose_name="User", attrs={
        "td": {"class": "text-secondary"}
    })
    session = tables.Column(verbose_name="Session", attrs={
        "td": {"class": "text-secondary"}
    })
    status_code = tables.Column(verbose_name="Status Code", attrs={
        "td": {"class": "fw-bold"}
    })
    exit_code = tables.Column(verbose_name="Exit Code", attrs={
        "td": {"class": "text-center"}
    })
    logs = tables.TemplateColumn(logs_column_template, verbose_name="Logs")
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": header_checkbox_hyperscript,
                "class": "form-check-input form-check-lg"  # Makes the checkbox bigger
            },
            "td__input": {
                "class": "form-check-input form-check-lg",  # Makes the checkbox bigger in rows
                "style": "transform: scale(1.5);",  # Further increase checkbox size
            }
        },
    )

    class Meta:
        orderable = False
        attrs = {"class": "table table-striped table-hover"}

    def render_status_code(self, value):
        """Render the status_code with larger, more visible badges."""
        if value == "DEAD":
            return mark_safe(f'<span class="badge bg-danger px-3 py-2 rounded" style="font-size: 1.1rem;">DEAD</span>')
        elif value == "RUNNING":
            return mark_safe(f'<span class="badge bg-success px-3 py-2 rounded" style="font-size: 1.1rem;">RUNNING</span>')
        return mark_safe(f'<span class="badge bg-secondary px-3 py-2 rounded" style="font-size: 1.1rem;">{value}</span>')

    def render_select(self, value: str) -> str:
        """Customise behaviour of checkboxes in the select column.

        This method is overriding the default render behavior for the CheckBoxColumn. 
        We use `mark_safe` to ensure that the generated HTML for the checkbox, 
        including the required `hx-preserve` and hyperscript logic, is rendered safely.
        """
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            f'hx-preserve="true" class="form-check-input form-check-lg row-checkbox" style="transform: scale(1.5);" _="{row_checkbox_hyperscript}">'
        )
