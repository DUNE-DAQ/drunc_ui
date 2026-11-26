"""View functions for runconf pages."""

import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_POST

from drunc_ui.runconf.configuration import (
    create_run_config,
    get_production_config,
    list_production_configs,
)

TEMPLATE = "runconf/config_view.html"


def _selection_context(params: QueryDict) -> dict[str, Any]:
    """Validate the version and session in ``params`` and build the page context."""
    listing = list_production_configs()
    daq_versions = [listing["daq_version"]]
    configs = {
        json.dumps([config["file"], config["session_id"]]): config for config in listing["configs"]
    }
    selected_version = params.get("daq_version", "")
    selected_session = params.get("session", "")
    selection_error = ""

    if selected_version and selected_version not in daq_versions:
        selection_error = "Select an available DAQ version."
        selected_version = ""
        selected_session = ""
    if selected_session and not selected_version:
        selection_error = "Select a DAQ version before selecting a session."
        selected_session = ""
    elif selected_session and selected_session not in configs:
        selection_error = "Select an available session for this DAQ version."
        selected_session = ""

    sessions = []
    if selected_version:
        sessions = [
            {"value": key, "label": f"{config['session_id']} ({config['file']})"}
            for key, config in configs.items()
        ]

    selected_config = None
    if selected_session:
        config = configs[selected_session]
        working_copy = get_production_config(config["file"], config["session_id"])
        selected_config = {
            "daq_config": working_copy["path"],
            "current_config_file": working_copy["working_path"],
            "session_in_config": working_copy["session_id"],
            "tree": json.dumps(working_copy["tree"], indent=2, ensure_ascii=False),
        }

    return {
        "apparatus": listing["apparatus"],
        "daq_versions": daq_versions,
        "sessions": sessions,
        "selected_version": selected_version,
        "selected_session": selected_session,
        "selected_config": selected_config,
        "selection_error": selection_error,
    }


@login_required
def config_view(request: HttpRequest) -> HttpResponse:
    """View that renders the configuration selection and display page."""
    context = _selection_context(request.GET)
    return render(request=request, template_name=TEMPLATE, context=context)


@login_required
@require_POST
def create_config(request: HttpRequest) -> HttpResponse:
    """Create a run configuration from the selected working copy."""
    context = _selection_context(request.POST)
    selected_config = context["selected_config"]
    if selected_config is None:
        if not context["selection_error"]:
            context["selection_error"] = (
                "Select a configuration before creating a run configuration."
            )
    else:
        context["created_config"] = create_run_config(
            selected_config["current_config_file"], selected_config["session_in_config"]
        )
    return render(request=request, template_name=TEMPLATE, context=context)
