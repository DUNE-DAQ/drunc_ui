"""View utilities."""

import logging
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

ViewType = Callable[[HttpRequest], HttpResponse] | Callable[[HttpRequest, str], HttpResponse]


def handle_errors(view_func: ViewType) -> ViewType:
    """Decorator to handle errors. Must decorate a view function.

    Args:
        view_func: The The view function to be wrapped.

    Returns:
        The wrapped view function.
    """

    def wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:  # type: ignore
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception(e)
            context = {"error_message": f"An error occurred: {e}"}
            return render(request, "main/error_message.html", context=context)

    return wrapped_view
