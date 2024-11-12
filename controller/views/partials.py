"""Partial views module for the controller app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..fsm import DruncFSM
from ..tables import FSMTable


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)

    # TODO: Remove this once the controller is implemented
    state = request.POST.get("current_state", "None")

    fsm = DruncFSM.get(state)
    if event:
        fsm.send(event)

    table = FSMTable.from_dict(fsm.to_dict(), fsm.current_state.name)

    return render(
        request=request,
        context=dict(
            events=[t.event for t in fsm.current_state.transitions],
            current_state=fsm.current_state.name,
            table=table,
        ),
        template_name="controller/partials/state_machine.html",
    )
