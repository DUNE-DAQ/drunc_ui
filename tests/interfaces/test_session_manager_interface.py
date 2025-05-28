def test_get_configs(mocker):
    """Test the get_configs function."""
    from dataclasses import dataclass

    from interfaces.session_manager_interface import get_configs

    @dataclass
    class Config:
        file: str
        session_id: str

    class Configs:
        config_keys = (
            Config("somefile.txt", "42"),
            Config("another_file.txt", "42+1"),
        )

    class MockSessionManager:
        data = Configs()

        def list_all_configs(self):
            return self

    mock = mocker.patch(
        "interfaces.session_manager_interface.get_session_manager_driver"
    )
    mock.return_value = MockSessionManager()

    configs = get_configs()
    assert all(
        "file" in config.keys() and "session_id" in config.keys() for config in configs
    )


def test_get_sessions(mocker):
    """Test the get_sessions function."""
    from dataclasses import dataclass

    from interfaces.session_manager_interface import get_sessions

    @dataclass
    class Session:
        name: str
        user: str

    class Sessions:
        active_sessions = (Session("Grey", "Gandalf"), Session("Brown", "Radagast"))

    class MockSessionManager:
        data = Sessions()

        def list_all_sessions(self):
            return self

    mock = mocker.patch(
        "interfaces.session_manager_interface.get_session_manager_driver"
    )
    mock.return_value = MockSessionManager()

    sessions = get_sessions()
    assert all(
        "name" in session.keys() and "actor" in session.keys() for session in sessions
    )
