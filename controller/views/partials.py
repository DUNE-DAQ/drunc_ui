"""Partial views module for the controller app."""

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..app_tree import AppTree
from ..fsm import DruncFSM
from ..tables import FSMTable


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Renders the state machine view."""
    event = request.POST.get("event", None)
    kwargs: dict[str, Any] = {  # type: ignore[misc]
        k: v
        for k, v in request.POST.items()
        if k not in ["csrfmiddlewaretoken", "event", "current_state"]
    }

    # TODO: Remove this once the controller is implemented
    state = request.POST.get("current_state", "None")

    fsm = DruncFSM.get(state)
    if event:
        fsm.send(event, **kwargs)

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


@login_required
def dialog(request: HttpRequest) -> HttpResponse:
    """Renders the arguments dialog view."""
    event = request.POST.get("event", None)

    # TODO: Remove this once the controller is implemented
    state = request.POST.get("current_state", "None")

    # TODO: Remove this and pull the arguments from the controller, once implemented
    args = ["arg1", "arg2", "arg3"]

    context = dict(
        current_state=state,
        event=event,
        args=args,
    )

    return render(
        request=request,
        context=context,
        template_name="controller/partials/arguments_dialog.html",
    )


@login_required
def app_tree_view(request: HttpRequest) -> HttpResponse:
    """Renders the app tree view."""
    tree = AppTree.from_drunc()
    return render(
        request=request,
        context=dict(tree=tree.to_shoelace_tree()),
        template_name="controller/partials/app_tree.html",
    )
