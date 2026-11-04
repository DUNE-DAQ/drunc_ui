"""View functions for runconf pages."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def config_view(request: HttpRequest) -> HttpResponse:
    """View that renders the configuration selection and display page."""
    # Placeholder catalogue until configuration repositories are connected.
    sessions_by_version = {
        "v1.0.0": ["np02-session", "np02-calibration"],
        "v1.1.0": ["np02-session", "np02-calibration", "np02-test"],
        "v1.2.0": ["np02-session", "np02-test"],
    }
    selected_version = request.GET.get("daq_version", "")
    selected_session = request.GET.get("session", "")
    selection_error = ""
    if selected_version and selected_version not in sessions_by_version:
        selection_error = "Select an available DAQ version."
        selected_version = ""
        selected_session = ""

    sessions = sessions_by_version.get(selected_version, [])
    if selected_session and not selected_version:
        selection_error = "Select a DAQ version before selecting a session."
        selected_session = ""
    elif selected_session and selected_session not in sessions:
        selection_error = "Select an available session for this DAQ version."
        selected_session = ""

    selected_config = None
    if selected_version and selected_session:
        selected_config = {
            "apparatus": "np02",
            "daq_config": f"base-configs/{selected_version}/{selected_session}.data.xml",
            "current_config_file": (
                f"shifter-configs/{selected_version}/{selected_session}.data.xml"
            ),
            "session_in_config": selected_session,
        }

    context = {
        "daq_versions": list(sessions_by_version),
        "sessions": sessions,
        "selected_version": selected_version,
        "selected_session": selected_session,
        "selected_config": selected_config,
        "selection_error": selection_error,
    }

    return render(request=request, template_name="runconf/config_view.html", context=context)
