"""View utilities."""

import logging
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def handle_errors(
    view_func: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    """Decorator to handle errors.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        The wrapped view function.
    """
    logger = logging.getLogger("django")

    def wrapped_view(request, *args, **kwargs) -> HttpResponse:  # type: ignore
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return render(request, "main/error_message.html")

    return wrapped_view
