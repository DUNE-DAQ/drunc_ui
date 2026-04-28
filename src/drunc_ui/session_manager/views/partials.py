"""Module for the partial views of the session manager."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from drunc_ui.interfaces import session_manager_interface as smi
from drunc_ui.main.views.utils import handle_errors

from .. import tables


@login_required
@handle_errors
def active_sessions_table_view(request: HttpRequest) -> HttpResponse:
    """View that renders the active sessions table."""
    return render(
        request=request,
        context=dict(table=tables.ActiveSessions(smi.get_sessions())),
        template_name="session_manager/partials/table_partial.html",
    )


@login_required
@handle_errors
def available_configs_table_view(request: HttpRequest) -> HttpResponse:
    """View that renders the available configs table."""
    return render(
        request=request,
        context=dict(table=tables.AvailableConfigs(smi.get_configs())),
        template_name="session_manager/partials/table_partial.html",
    )
