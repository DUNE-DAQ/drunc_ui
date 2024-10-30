"""Module providing functions to interact with the drunc controller."""

from django.conf import settings
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname
from druncschema.request_response_pb2 import Description


def get_controller_driver() -> ControllerDriver:
    """Get a ControllerDriver instance."""
    token = create_dummy_token_from_uname()
    return ControllerDriver(settings.ROOT_CONTROLLER_URL, token=token, aio_channel=True)


def get_controller_status() -> Description:
    """Get the controller status."""
    return get_controller_driver().get_status()
