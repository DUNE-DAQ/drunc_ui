"""Module providing functions to interact with the drunc controller."""

import functools
from enum import IntEnum
from typing import Any

from django.conf import settings
from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.grpc_utils import pack_to_any
from drunc.utils.shell_utils import create_dummy_token_from_uname
from drunc.utils.utils import get_control_type_and_uri_from_connectivity_service
from druncschema.controller_pb2 import Argument, FSMCommand, FSMResponseFlag
from druncschema.generic_pb2 import bool_msg, float_msg, int_msg, string_msg
from druncschema.request_response_pb2 import Description


class Presence(IntEnum):
    """Enum to represent the presence of an argument."""

    MANDATORY = 0
    OPTIONAL = 1


class FieldType(IntEnum):
    """Enum to represent the type of an argument."""

    INT = 0
    FLOAT = 1
    STRING = 2
    BOOL = 3


@functools.cache
def get_controller_uri() -> str:
    """Find where the root controller is running via the connectivity service.

    Returns:
        str: The URI of the root controller.
    """
    csc = ConnectivityServiceClient(settings.CSC_SESSION, settings.CSC_URL)
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


def send_event(  # type: ignore[misc]
    event: str,
    arguments: dict[str, Any],
) -> FSMResponseFlag:
    """Send an event to the controller.

    Args:
        event: The event to send.
        arguments: The arguments for the event.

    Returns:
        FSMResponseFlag: The flag returned by the controller. 0 if the event was
            successful, 1-4 if the event failed.
    """
    controller = get_controller_driver()
    controller.take_control()
    command = FSMCommand(
        command_name=event, arguments=process_arguments(event, arguments)
    )
    return controller.execute_fsm_command(command).flag


def get_arguments(event: str) -> list[Argument]:
    """Get the arguments required to run an event.

    Args:
        event: The event to get the arguments for.

    Returns:
        The arguments for the event.
    """
    controller = get_controller_driver()
    events = controller.describe_fsm().data.commands
    try:
        command = next(c for c in events if c.name == event)
    except StopIteration:
        raise ValueError(
            f"Event '{event}' not found in FSM. Valid events are: "
            f"{', '.join(c.name for c in events)}"
        )
    return command.arguments


def process_arguments(  # type: ignore[misc]
    event: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Process the arguments for an event.

    Args:
        event: The event to process.
        arguments: The arguments to process.

    Returns:
        dict: The processed arguments in a form compatible with the protobuf definition.
    """
    valid_args = get_arguments(event)
    processed = {}
    for arg in valid_args:
        if arg.name not in arguments or arguments[arg.name] is None:
            continue

        match arg.type:
            case FieldType.INT:
                processed[arg.name] = pack_to_any(int_msg(value=arguments[arg.name]))
            case FieldType.FLOAT:
                processed[arg.name] = pack_to_any(float_msg(value=arguments[arg.name]))
            case FieldType.STRING:
                processed[arg.name] = pack_to_any(string_msg(value=arguments[arg.name]))
            case FieldType.BOOL:
                processed[arg.name] = pack_to_any(bool_msg(value=arguments[arg.name]))

    return processed
