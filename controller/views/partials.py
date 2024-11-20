"""Partial views module for the controller app."""

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .. import controller_interface as ci
from .. import fsm, tables


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)
    kwargs: dict[str, Any] = {  # type: ignore[misc]
        k: v
        for k, v in request.POST.items()
        if k not in ["csrfmiddlewaretoken", "event", "current_state"]
    }

    if event:
        ci.send_event(event, **kwargs)

    table = tables.FSMTable.from_dict(fsm.get_fsm_architecture(), ci.get_fsm_state())

    return render(
        request=request,
        context=dict(table=table),
        template_name="controller/partials/state_machine.html",
    )


@login_required
def dialog(request: HttpRequest) -> HttpResponse:
    """Dialog to gather the input arguments required by the event."""
    event = request.POST.get("event", None)

    args = []
    if event:
        args = ci.get_arguments(event)

    return render(
        request=request,
        context=dict(
            event=event,
            args=args,
        ),
        template_name="controller/partials/arguments_dialog.html",
    )
