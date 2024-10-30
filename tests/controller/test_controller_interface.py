def test_get_controller_status(mocker):
    """Test the _boot_process function."""
    from controller.controller_interface import get_controller_status

    mock = mocker.patch("controller.controller_interface.get_controller_driver")
    get_controller_status()
    mock.assert_called_once()
