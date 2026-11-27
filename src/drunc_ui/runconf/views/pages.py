"""View functions for runconf pages."""

import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_POST

from drunc_ui.runconf.runconf_backend_placeholder import MockRunconfService, get_runconf_service

TEMPLATE = "runconf/config_view.html"

# runconfschema returns only the created file's path, so drunc_ui builds the
# command that boots it.
DRUNC_PROCESS_MANAGER = "ssh-standalone"
DRUNC_SESSION_NAME = "mock-session"


def _selection_context(params: QueryDict) -> tuple[dict[str, Any], MockRunconfService]:
    """Replay the version and session in ``params`` on the server, and build the page context.

    Returns the context and the server, which holds the opened configuration.
    """
    service = get_runconf_service()
    initialisation = service.initialise()
    dropdowns = initialisation["dropdowns"]
    selected_version = params.get("daq_version", "")
    selected_session = params.get("session", "")
    selection_error = ""

    if selected_version:
        update = service.select_dropdown({"key": "version", "value": selected_version})
        dropdowns = update["update"]
        if update["response"]["outcome"] != "SUCCESS":
            selection_error = "Select an available DAQ version."
            selected_version = ""
            selected_session = ""
    if selected_session and not selected_version:
        selection_error = "Select a DAQ version before selecting a session."
        selected_session = ""
    elif selected_session:
        update = service.select_dropdown({"key": "session", "value": selected_session})
        dropdowns = update["update"]
        if update["response"]["outcome"] != "SUCCESS":
            selection_error = "Select an available session for this DAQ version."
            selected_session = ""

    selected_config = None
    if selected_session:
        outcome = service.open_configuration(
            {"selection": {"version": selected_version, "session": selected_session}}
        )
        if outcome["response"]["outcome"] == "SUCCESS":
            info = service.get_configuration_info()
            selected_config = {
                "daq_config": info.get("config_file", ""),
                "current_config_file": info.get("current_file", ""),
                "session_in_config": info.get("session_name", ""),
                "tree": json.dumps(info["config_tree"], indent=2, ensure_ascii=False),
            }
        else:
            selection_error = outcome["response"].get("message", "Failed to open configuration.")
            selected_session = ""

    context = {
        "apparatus": initialisation["apparatus"],
        "daq_versions": dropdowns["version"]["values"],
        "sessions": dropdowns["session"]["values"] if selected_version else [],
        "selected_version": selected_version,
        "selected_session": selected_session,
        "selected_config": selected_config,
        "selection_error": selection_error,
    }
    return context, service


@login_required
def config_view(request: HttpRequest) -> HttpResponse:
    """View that renders the configuration selection and display page."""
    context, _ = _selection_context(request.GET)
    return render(request=request, template_name=TEMPLATE, context=context)


@login_required
@require_POST
def create_config(request: HttpRequest) -> HttpResponse:
    """Create a run configuration from the opened configuration."""
    context, service = _selection_context(request.POST)
    selected_config = context["selected_config"]
    if selected_config is None:
        if not context["selection_error"]:
            context["selection_error"] = (
                "Select a configuration before creating a run configuration."
            )
        return render(request=request, template_name=TEMPLATE, context=context)

    created = service.runconf_command({"command": "CREATE_QUIT"})
    # CREATE_QUIT details are a StringValue holding the created file's path.
    path = created.get("details", {"@type": ""}).get("value")
    if created["response"]["outcome"] != "SUCCESS" or path is None:
        context["selection_error"] = created["response"].get(
            "message", "Failed to create the run configuration."
        )
        return render(request=request, template_name=TEMPLATE, context=context)

    session_name = selected_config["session_in_config"]
    context["created_config"] = {
        "session_id": session_name,
        "source_path": selected_config["current_config_file"],
        "path": path,
        "drunc_command": (
            f"drunc-unified-shell {DRUNC_PROCESS_MANAGER} {path} {session_name} "
            f"{DRUNC_SESSION_NAME}"
        ),
    }
    return render(request=request, template_name=TEMPLATE, context=context)
