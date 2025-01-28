from django.conf import settings
from druncschema.process_manager_pb2 import LogRequest, ProcessQuery, ProcessUUID
from druncschema.token_pb2 import Token

from interfaces.process_manager_interface import (
    boot_process,
    get_process_logs,
    get_process_manager_driver,
)


def test_get_process_manager_driver(mocker):
    """Test the get_process_manager_driver function."""
    mock_driver = mocker.patch(
        "process_manager.process_manager_interface.ProcessManagerDriver"
    )

    username = "testuser"
    driver = get_process_manager_driver(username)

    # Verify that ProcessManagerDriver was called with the correct arguments
    expected_token = Token(token=f"{username}-token", user_name=username)
    mock_driver.assert_called_once_with(
        settings.PROCESS_MANAGER_URL,
        token=expected_token,
        aio_channel=True,
    )

    # Verify that the function returns the mock driver instance
    assert driver == mock_driver.return_value


def test_boot_process(mock_get_process_manager_driver, dummy_session_data):
    """Test the boot_process function."""
    mock_driver = mock_get_process_manager_driver
    boot_process("root", dummy_session_data)
    mock_driver.assert_called_once_with("root")
    mock_driver.return_value.dummy_boot.assert_called_once_with(
        user="root", **dummy_session_data
    )


def test_get_process_logs(mock_get_process_manager_driver):
    """Test the get_process_logs function."""
    mock_driver = mock_get_process_manager_driver
    get_process_logs("1234", "root")

    mock_driver.assert_called_once_with("root")
    mock_logs = mock_driver.return_value.logs

    query = ProcessQuery(uuids=[ProcessUUID(uuid="1234")])
    request = LogRequest(query=query, how_far=100)
    mock_logs.assert_called_once_with(request)
