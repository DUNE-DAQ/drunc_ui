"""View functions for runconf pages."""

import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from drunc.utils.grpc_utils import ServerUnreachable
from grpc import RpcError

from drunc_ui.interfaces import session_manager_interface as smi
from drunc_ui.runconf.configuration import load_config


@login_required
def config_view(request: HttpRequest) -> HttpResponse:
    """View that renders the configuration selection and display page."""
    version = os.environ.get("SPACK_RELEASE", "")
    daq_versions = [version] if version else []
    selected_version = request.GET.get("daq_version", "")
    selected_session = request.GET.get("session", "")
    selection_error = (
        "" if version else "SPACK_RELEASE is not set. Start drunc-ui in the DBT environment."
    )
    if selected_version and selected_version not in daq_versions:
        selection_error = "Select an available DAQ version."
        selected_version = ""
        selected_session = ""

    sessions = []
    configs = {}
    if selected_version:
        try:
            for config in smi.get_configs():
                key = json.dumps([config["file"], config["session_id"]])
                configs[key] = config
            sessions = [
                {"value": key, "label": f"{config['session_id']} ({config['file']})"}
                for key, config in configs.items()
            ]
            if not sessions:
                selection_error = "The SessionManager returned no available configurations."
        except (ServerUnreachable, RpcError) as error:
            logging.getLogger("django").exception("Unable to retrieve runconf configurations")
            selection_error = f"Unable to retrieve configurations from the SessionManager: {error}"
    if selected_session and not selected_version:
        selection_error = "Select a DAQ version before selecting a session."
        selected_session = ""
    elif selected_session and selected_session not in configs:
        if not selection_error:
            selection_error = "Select an available session for this DAQ version."
        selected_session = ""

    selected_config = None
    if selected_version and selected_session:
        config = configs[selected_session]
        try:
            selected_config = load_config(config["file"], config["session_id"])
        except (OSError, ValueError, RuntimeError) as error:
            logging.getLogger("django").exception("Unable to load local runconf configuration")
            selection_error = f"Unable to load configuration: {error}"

    context = {
        "daq_versions": daq_versions,
        "sessions": sessions,
        "selected_version": selected_version,
        "selected_session": selected_session,
        "selected_config": selected_config,
        "selection_error": selection_error,
    }

    return render(request=request, template_name="runconf/config_view.html", context=context)
