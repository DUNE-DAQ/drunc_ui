"""Executable entry points for drunc-ui."""

import os
import sys


def _configure_django() -> None:
    """Use the caller's settings module if set, otherwise use the project default."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drunc_ui.settings.settings")


def manage() -> None:
    """Run Django management commands."""
    _configure_django()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


def run_gunicorn() -> None:
    """Run the drunc-ui WSGI application with Gunicorn."""
    _configure_django()

    from gunicorn.app.wsgiapp import run

    sys.argv = [
        sys.argv[0],
        "drunc_ui.wsgi:application",
        *sys.argv[1:],
    ]

    run()
