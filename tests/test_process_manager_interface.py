from druncschema.process_manager_pb2 import LogRequest, ProcessQuery, ProcessUUID

from process_manager.process_manager_interface import boot_process, get_process_logs


def test_boot_process(mocker, dummy_session_data):
    """Test the _boot_process function."""
    mock = mocker.patch(
        "process_manager.process_manager_interface.get_process_manager_driver"
    )
    boot_process("root", dummy_session_data)
    mock.assert_called_once()
    mock.return_value.dummy_boot.assert_called_once_with(
        user="root", **dummy_session_data
    )


def test_get_process_logs(mocker):
    """Test the get_process_logs function."""
    mock_driver = mocker.patch(
        "process_manager.process_manager_interface.get_process_manager_driver"
    )
    get_process_logs("1234", "root")

    mock_driver.assert_called_once()
    mock_logs = mock_driver.return_value.logs

    query = ProcessQuery(uuids=[ProcessUUID(uuid="1234")])
    request = LogRequest(query=query, how_far=100)
    mock_logs.assert_called_once_with(request)
