from django.conf import settings
from druncschema.process_manager_pb2 import LogRequest, ProcessQuery, ProcessUUID
from druncschema.token_pb2 import Token

from drunc_ui.interfaces.process_manager_interface import (
    boot_process,
    get_process_logs,
    get_process_manager_driver,
)


def test_get_process_manager_driver(mocker):
    """Test the get_process_manager_driver function."""
    mock_driver = mocker.patch("drunc_ui.interfaces.process_manager_interface.ProcessManagerDriver")

    username = "testuser"
    driver = get_process_manager_driver(username)

    # Verify that ProcessManagerDriver was called with the correct arguments
    expected_token = Token(token=f"{username}-token", user_name=username)
    mock_driver.assert_called_once_with(
        settings.PROCESS_MANAGER_URL,
        token=expected_token,
    )

    # Verify that the function returns the mock driver instance
    assert driver == mock_driver.return_value


def test_boot_process(mocker):
    """Test the boot_process function."""
    session_name = "sess_name"
    n_processes = 1
    sleep = 5
    n_sleeps = 4

    mock = mocker.patch("drunc_ui.interfaces.process_manager_interface.get_process_manager_driver")

    boot_process("root", session_name, n_processes, sleep, n_sleeps)

    mock.assert_called_once_with("root")
    mock.return_value.dummy_boot.assert_called_once_with(
        "root", session_name, n_processes, sleep, n_sleeps
    )


def test_get_process_logs(mocker):
    """Test the get_process_logs function."""
    query = ProcessQuery(uuids=[ProcessUUID(uuid="1234")])
    request = LogRequest(query=query, how_far=100)

    mock = mocker.patch("drunc_ui.interfaces.process_manager_interface.get_process_manager_driver")

    get_process_logs("1234", "root")

    mock.assert_called_once_with("root")
    mock.return_value.logs.assert_called_once_with(request)
