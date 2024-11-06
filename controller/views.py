"""Views module for the controller app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .fsm import DruncFSM


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View that renders the index/home page."""
    return render(request=request, template_name="controller/index.html")


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)
    state = request.POST.get("current_state", "none")

    fsm = DruncFSM(start_value=state.lower())
    if event:
        fsm.send(event)

    states = fsm.to_dict()

    return render(
        request=request,
        context=dict(
            states=states,
            current_state=fsm.current_state.name,
        ),
        template_name="controller/state_machine.html",
    )
