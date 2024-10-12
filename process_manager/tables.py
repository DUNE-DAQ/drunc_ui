"""Tables for the process_manager app."""

import django_tables2 as tables

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\">LOGS</a>"
)


class ProcessTable(tables.Table):
    """Defines and Process Table for the data from the Process Manager."""

    class Meta:  # noqa: D106
        orderable = False

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
        checked="checked",
        attrs={"th__input": {"onclick": "toggle(this)"}},
    )
