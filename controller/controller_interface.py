"""Module providing functions to interact with the drunc controller."""

from django.conf import settings
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname
from druncschema.controller_pb2 import FSMResponseFlag, Status


def get_controller_driver() -> ControllerDriver:
    """Get a ControllerDriver instance."""
    token = create_dummy_token_from_uname()
    return ControllerDriver(settings.ROOT_CONTROLLER_URL, token=token, aio_channel=True)


def get_controller_status() -> Status:
    """Get the controller state.

    Returns:
        str: The controller state.
    """
    return get_controller_driver().get_status().data


def get_fsm_state() -> str:
    """Get the finite state machine state.

    Returns:
        str: The state the FSM is in.
    """
    return get_controller_status().state


def send_event(event: str, **kwargs: dict[str, str]) -> FSMResponseFlag:
    """Send an event to the controller.

    Args:
        event (str): The event to send.
        **kwargs (dict[str, str]): The arguments for the event.

    Returns:
        FSMResponseFlag: The flag returned by the controller. 0 if the event was
            successful, 1-4 if the event failed.
    """
    return get_controller_driver().execute_fsm_command(event, **kwargs).data.flag
