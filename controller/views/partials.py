"""Partial views module for the controller app."""

from typing import Any, cast

from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import SafeString, mark_safe

from .. import controller_interface as ci
from .. import forms, fsm, tables
from ..app_tree import AppType


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)
    arguments: dict[str, Any] = {  # type: ignore[misc]
        k: v
        for k, v in request.POST.items()
        if k not in ["csrfmiddlewaretoken", "event"]
    }
    if event:
        form = forms.get_form_for_event(event)(arguments)
        if form.is_valid():
            ci.send_event(event, form.cleaned_data)
        else:
            raise ValueError(f"Invalid form: {form.errors}")

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

    form = forms.get_form_for_event(event)() if event else Form()
    has_args = len(form.fields) > 0

    return render(
        request=request,
        context=dict(
            event=event,
            has_args=has_args,
            form=form,
        ),
        template_name="controller/partials/arguments_dialog.html",
    )


def app_to_shoelace_tree(app: AppType) -> SafeString:
    """Convert the app tree to a format compatible with the shoelace tree component.

    Args:
        app: The app tree to convert.

    Returns:
        The shoelace tree component as safe HTML code.
    """
    return mark_safe(
        f"<sl-tree-item expanded> {app.name}"
        + "".join(app_to_shoelace_tree(child) for child in app.children)
        + "</sl-tree-item>"
    )


@login_required
def app_tree_view_summary(request: HttpRequest) -> HttpResponse:
    """Renders the app tree view summary."""
    return render(
        request=request,
        context=dict(tree=app_to_shoelace_tree(ci.get_app_tree(request.user.username))),
        template_name="controller/partials/app_tree_summary_partial.html",
    )


@login_required
def app_tree_view_table(request: HttpRequest) -> HttpResponse:
    """View that renders the app tree view table."""
    table = tables.AppTreeTable(ci.get_app_tree(request.user.username).to_list())
    return render(
        request=request,
        context=dict(table=table),
        template_name="controller/partials/app_tree_table_partial.html",
    )
