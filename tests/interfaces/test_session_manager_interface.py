def test_get_configs(mocker):
    """Test the get_configs function."""
    from druncschema.session_manager_pb2 import AllConfigKeys

    from drunc_ui.interfaces.session_manager_interface import get_configs

    class MockSessionManagerDriver:
        def list_all_configs(self):
            response = AllConfigKeys()
            config1 = response.config_keys.add()
            config1.file = "somefile.txt"
            config1.session_id = "42"
            config2 = response.config_keys.add()
            config2.file = "another_file.txt"
            config2.session_id = "42+1"
            return response

    mock = mocker.patch("drunc_ui.interfaces.session_manager_interface.get_session_manager_driver")
    mock.return_value = MockSessionManagerDriver()

    configs = get_configs()
    assert all("file" in config.keys() and "session_id" in config.keys() for config in configs)


def test_get_sessions(mocker):
    """Test the get_sessions function."""
    from druncschema.session_manager_pb2 import AllActiveSessions

    from drunc_ui.interfaces.session_manager_interface import get_sessions

    class MockSessionManagerDriver:
        def list_all_sessions(self):
            response = AllActiveSessions()
            session1 = response.active_sessions.add()
            session1.name = "Grey"
            session1.user = "Gandalf"
            session2 = response.active_sessions.add()
            session2.name = "Brown"
            session2.user = "Radagast"
            return response

    mock = mocker.patch("drunc_ui.interfaces.session_manager_interface.get_session_manager_driver")
    mock.return_value = MockSessionManagerDriver()

    sessions = get_sessions()
    assert all("name" in session.keys() and "actor" in session.keys() for session in sessions)
