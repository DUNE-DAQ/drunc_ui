"""Module for the partial views of the session manager."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from interfaces import controller_interface as ci

from .. import tables


@login_required
def active_sessions_table_view(request: HttpRequest) -> HttpResponse:
    """View that renders the active sessions table."""
    return render(
        request=request,
        context=dict(table=tables.ActiveSessions(ci.get_sessions())),
        template_name="session_manager/partials/table_partial.html",
    )


@login_required
def available_configs_table_view(request: HttpRequest) -> HttpResponse:
    """View that renders the available configs table."""
    return render(
        request=request,
        context=dict(table=tables.AvailableConfigs(ci.get_configs())),
        template_name="session_manager/partials/table_partial.html",
    )
