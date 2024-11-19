"""Module providing functions to interact with the drunc controller."""

from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname
from druncschema.controller_pb2 import FSMResponseFlag
from drunc.utils.utils import get_control_type_and_uri_from_connectivity_service
from druncschema.request_response_pb2 import Description


def get_controller_uri() -> str:
    """Find where the root controller is running via the connectivity service.

    Returns:
        str: The URI of the root controller.
    """
    csc = ConnectivityServiceClient("local-2x3-config", "drunc:5000")
    _, uri = get_control_type_and_uri_from_connectivity_service(
        csc,
        name="root-controller",
    )
    return uri


def get_controller_driver() -> ControllerDriver:
    """Get a ControllerDriver instance."""
    uri = get_controller_uri()
    token = create_dummy_token_from_uname()
    return ControllerDriver(uri, token=token)


def get_controller_status() -> Description:
    """Get the controller status."""
    return get_controller_driver().status()


def get_fsm_state() -> str:
    """Get the finite state machine state.

    Returns:
        str: The state the FSM is in.
    """
    return get_controller_status().data.state


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
