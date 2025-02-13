"""Apps module for the session manager app."""

from django.apps import AppConfig


class SessionManagerConfig(AppConfig):
    """The app config for the session manager app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "session_manager"
