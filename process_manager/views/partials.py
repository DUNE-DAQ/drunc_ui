"""View functions for partials."""

import django_tables2
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.timezone import localtime
from druncschema.process_manager_pb2 import ProcessInstance
from main.models import DruncMessage

from ..process_manager_interface import get_session_info
from ..tables import ProcessTable


def filter_table(
    search: str, table: list[dict[str, str | int]]
) -> list[dict[str, str | int]]:
    """Filter table data based on search parameter.

    If the search parameter is empty, the table data is returned unfiltered. Otherwise,
    the table data is filtered based on the search parameter. The search parameter can
    be a string or a string with a column name and search string separated by a colon.
    If the search parameter is a column name, the search string is matched against the
    values in that column only. Otherwise, the search string is matched against all
    columns.

    Args:
        search: The search string to filter the table data.
        table: The table data to filter.

    Returns:
        The filtered table data.
    """
    if not search or not table:
        return table

    all_cols = list(table[0].keys())
    column, _, search = search.partition(":")
    if not search:
        # No column-based filtering
        search = column
        columns = all_cols
    elif column not in all_cols:
        # If column is unknown, search all columns
        columns = all_cols
    else:
        # Search only the specified column
        columns = [column]
    search = search.lower()
    return [row for row in table if any(search in str(row[k]).lower() for k in columns)]


@login_required
def process_table(request: HttpRequest) -> HttpResponse:
    """Renders the process table with sorting and filtering."""
    session_info = get_session_info()
    status_enum_lookup = dict(item[::-1] for item in ProcessInstance.StatusCode.items())

    # Build the table data
    table_data = [
        {
            "uuid": process_instance.uuid.uuid,
            "name": process_instance.process_description.metadata.name,
            "user": process_instance.process_description.metadata.user,
            "session": process_instance.process_description.metadata.session,
            "status_code": status_enum_lookup[process_instance.status_code],
            "exit_code": process_instance.return_code,
        }
        for process_instance in session_info.data.values
    ]

    # Apply search filtering
    table_data = filter_table(request.GET.get("search", ""), table_data)
    table = ProcessTable(table_data)

    # Set the order based on the 'sort' parameter in the GET request, defaulting to 'uuid'
    sort_param = request.GET.get("sort", "")
    table.order_by = sort_param
    sort_param = request.GET

    return render(
        request=request,
        context={"table": table, "sort_param": sort_param},
        template_name="process_manager/partials/process_table.html",
    )


@login_required
def messages(request: HttpRequest) -> HttpResponse:
    """Search and render Kafka messages from the database."""
    search = request.GET.get("search", "")
    records = DruncMessage.objects.filter(
        topic__regex=settings.KAFKA_TOPIC_REGEX["PROCMAN"], message__icontains=search
    )

    # Time is stored as UTC. localtime(t) converts this to our configured timezone.
    messages = [
        f"{localtime(record.timestamp).strftime('%Y-%m-%d %H:%M:%S')}: {record.message}"
        for record in records
    ]

    return render(
        request=request,
        context=dict(messages=messages[::-1]),
        template_name="process_manager/partials/message_items.html",
    )
