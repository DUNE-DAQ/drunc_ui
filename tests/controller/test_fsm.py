def test_drunc_fsm_get(mocker):
    """Test the DruncFSM.get method."""
    from controller.fsm import DruncFSM

    mock_get_fsm_state = mocker.patch("controller.controller_interface.get_fsm_state")
    mock_get_fsm_state.return_value = "None"

    DruncFSM.get()
    mock_get_fsm_state.assert_called_once()
    mock_get_fsm_state.reset_mock()

    fsm = DruncFSM.get("configured")
    mock_get_fsm_state.assert_not_called()

    assert fsm.current_state.name == "Configured"


def test_drunc_fsm_to_dict():
    """Test the DruncFSM.to_dict method."""
    from controller.fsm import DruncFSM

    fsm = DruncFSM.get("configured")
    fsm_dict = fsm.to_dict()

    assert len(fsm_dict) == len(DruncFSM.states)
    for state in DruncFSM.states:
        assert state.name in fsm_dict
        assert len(fsm_dict[state.name]) == len(state.transitions)
        for transition in fsm_dict[state.name]:
            assert transition["event"] in [t.event for t in state.transitions]
            assert transition["target"] in fsm_dict


def test_drunc_fsm_ordered_states():
    """Test the DruncFSM.ordered_states property."""
    from controller.fsm import DruncFSM

    fsm = DruncFSM.get("none")
    assert set(fsm.ordered_states) == {s.name for s in DruncFSM.states}
