def test_get_configs():
    """Test the get_configs function."""
    from interfaces.session_manager_interface import get_configs

    configs = get_configs()
    assert all("file" in config.keys() and "id" in config.keys() for config in configs)


def test_get_sessions():
    """Test the get_sessions function."""
    from interfaces.session_manager_interface import get_sessions

    sessions = get_sessions()
    assert all(
        "name" in session.keys() and "actor" in session.keys() for session in sessions
    )
