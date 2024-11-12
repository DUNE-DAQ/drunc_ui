"""Views module for the controller app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .fsm import DruncFSM
from .tables import FSMTable


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View that renders the index/home page."""
    return render(request=request, template_name="controller/index.html")


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)

    # TODO: Remove this once the controller is implemented
    state = request.POST.get("current_state", "None")

    fsm = DruncFSM.get(state.lower())
    if event:
        fsm.send(event)

    states = fsm.to_dict()
    table = FSMTable.from_dict(states, fsm.current_state.name)

    return render(
        request=request,
        context=dict(
            events=[t["event"] for t in states[fsm.current_state.name]],
            current_state=fsm.current_state.name,
            table=table,
        ),
        template_name="controller/state_machine.html",
    )
