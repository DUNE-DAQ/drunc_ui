"""View functions for partials."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from druncschema.process_manager_pb2 import ProcessInstance

from interfaces.process_manager_interface import get_session_info
from main.views.utils import handle_errors

from ..tables import ProcessTable


def filter_table(
    search: str, column: str, table: list[dict[str, str | int]]
) -> list[dict[str, str | int]]:
    """Filter table data based on search and column parameters.

    If the search parameter is empty, the table data is returned unfiltered. Otherwise,
    the table data is filtered based on the search parameter. If the column parameter
    is provided, the search string is matched against the values in that column only.
    If no valid column is specified, the search string is matched against all columns.

    Args:
        search: The search string to filter the table data.
        column: The column name to filter by, or an empty string to search all columns.
        table: The table data to filter.

    Returns:
        The filtered table data.
    """
    if not search or not table:
        return table

    all_cols = list(table[0].keys())
    columns = [column] if column in all_cols else all_cols

    # Convert search string to lowercase for case-insensitive matching
    search = search.lower()
    return [row for row in table if any(search in str(row[k]).lower() for k in columns)]


@login_required
@handle_errors
def process_table(request: HttpRequest) -> HttpResponse:
    """Renders the process table.

    This view may be called using either GET or POST methods. GET renders the table with
    no check boxes selected. POST renders the table with checked boxes for any table row
    with a uuid provided in the select key of the request data.
    """
    session_info = get_session_info(request.user.username)

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
        for process_instance in session_info.data.values  # type: ignore [attr-defined]
    ]
    # Get the values from the GET request
    search_dropdown = request.GET.get("search-drp", "")
    search_input = request.GET.get("search", "")

    # Determine the column and search values for filtering
    column = search_dropdown if search_dropdown else ""
    search = search_input if search_input else ""

    # Apply search filtering
    table_data = filter_table(search, column, table_data)
    table = ProcessTable(table_data)

    # Set the order based on the 'sort' parameter in the GET request, defaulting to ''
    sort_param = request.GET.get("sort", "")
    table.order_by = sort_param

    return render(
        request=request,
        context={"table": table},
        template_name="process_manager/partials/process_table.html",
    )
