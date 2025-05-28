"""Interface for the session manager endpoint."""

from django.conf import settings
from drunc.session_manager.session_manager_driver import SessionManagerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname


def get_session_manager_driver() -> SessionManagerDriver:
    """Get a ProcessManagerDriver instance."""
    token = create_dummy_token_from_uname()
    return SessionManagerDriver(
        settings.SESSION_MANAGER_URL, token=token, aio_channel=False
    )


def get_configs() -> list[dict[str, str]]:
    """Get the available configurations for the controller.

    Returns:
        List of dictionaries indicating the file where the config is contained and the
        id for the config.
    """
    configs = get_session_manager_driver().list_all_configs().data
    return [{"file": c.file, "session_id": c.session_id} for c in configs.config_keys]


def get_sessions() -> list[dict[str, str]]:
    """Get the active sessions in the controller.

    Returns:
        List of dictionaries indicating the session name and the actor name (i.e.
        typically, the user who boots the session).
    """
    sessions = get_session_manager_driver().list_all_sessions().data
    return [{"name": s.name, "user": s.user} for s in sessions.active_sessions]
