def test_get_controller_driver(mocker):
    """Test the get_controller_driver function."""
    mock_driver = mocker.patch("controller.controller_interface.ControllerDriver")
    mock_uri = mocker.patch("controller.controller_interface.get_controller_uri")
    mock_uri.return_value = "uri"
    mock_token = mocker.patch(
        "controller.controller_interface.create_dummy_token_from_uname"
    )
    mock_token.return_value = "token"

    from controller.controller_interface import get_controller_driver

    get_controller_driver()
    mock_uri.assert_called_once()
    mock_token.assert_called_once()
    mock_driver.assert_called_once_with("uri", token="token")


def test_get_controller_status(mocker):
    """Test the _boot_process function."""
    from controller.controller_interface import get_controller_status

    class MockControllerDriver:
        status = mocker.MagicMock()

    mock = mocker.patch("controller.controller_interface.get_controller_driver")
    mock.return_value = MockControllerDriver()
    get_controller_status()
    mock.assert_called_once()
    MockControllerDriver.status.assert_called_once()
