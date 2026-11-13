"""View functions for runconf pages."""

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from drunc_ui.runconf.configuration import get_production_config, list_production_configs


@login_required
def config_view(request: HttpRequest) -> HttpResponse:
    """View that renders the configuration selection and display page."""
    listing = list_production_configs()
    daq_versions = [listing["daq_version"]]
    configs = {
        json.dumps([config["file"], config["session_id"]]): config for config in listing["configs"]
    }
    selected_version = request.GET.get("daq_version", "")
    selected_session = request.GET.get("session", "")
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
            "contents": working_copy["contents"],
        }

    context = {
        "apparatus": listing["apparatus"],
        "daq_versions": daq_versions,
        "sessions": sessions,
        "selected_version": selected_version,
        "selected_session": selected_session,
        "selected_config": selected_config,
        "selection_error": selection_error,
    }

    return render(request=request, template_name="runconf/config_view.html", context=context)
