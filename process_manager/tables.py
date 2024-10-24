import django_tables2 as tables
from django.utils.safestring import mark_safe

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\" "
    "class=\"btn btn-sm btn-primary text-white\">LOGS</a>"
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

    uuid = tables.Column(verbose_name="UUID")
    name = tables.Column(verbose_name="Name")
    user = tables.Column(verbose_name="User")
    session = tables.Column(verbose_name="Session")
    status_code = tables.Column(verbose_name="Status Code")
    exit_code = tables.Column(verbose_name="Exit Code")
    logs = tables.TemplateColumn(logs_column_template, verbose_name="Logs")
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": header_checkbox_hyperscript,
            }
        },
    )

    class Meta:
        orderable = False

    def render_status_code(self, value):
        """Render the status_code with conditional formatting."""
        if value == "DEAD":
            return mark_safe(f'<span class="bg-danger text-white px-2 py-1 rounded">DEAD</span>')
        elif value == "RUNNING":
            return mark_safe(f'<span class="bg-success text-white px-2 py-1 rounded">RUNNING</span>')
        return value

    def render_select(self, value: str) -> str:
        """Customise behaviour of checkboxes in the select column.

        This method is overriding the default render behavior for the CheckBoxColumn. 
        We use `mark_safe` to ensure that the generated HTML for the checkbox, 
        including the required `hx-preserve` and hyperscript logic, is rendered safely.
        """
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            f'hx-preserve="true" class="row-checkbox" _="{row_checkbox_hyperscript}">'
        )
