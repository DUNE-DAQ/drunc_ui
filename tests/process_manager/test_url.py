from django.urls import Resolver404, resolve
from pytest import raises


def test_boot_process_url_not_available():
    """Test that the boot_process URL is not included when DEBUG is False.

    NOTE That tests are always run with DEBUG=False regardless of the actual
    setting, so this test is to ensure the view does not expose debug information
    in production.
    """
    with raises(Resolver404):
        resolve("process_manager:boot_process")
