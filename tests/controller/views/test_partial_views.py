from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse

from controller import fsm
from controller.tables import FSMTable

from ...utils import LoginRequiredTest


class TestFSMView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("controller:state_machine")

    def test_empty_post(self, auth_client, mocker):
        """Tests basic calls of view method."""
        mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
        mock_state.return_value = "initial"

        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        assert response.context["current_state"] == "initial"
        assert response.context["events"] == fsm.STATES["initial"]

    @pytest.mark.parametrize("state", fsm.STATES.keys())
    def test_non_empty_post(self, state, auth_client, mocker):
        """Tests basic calls of view method."""
        mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
        mocker.patch("controller.controller_interface.send_event")

        event = choice(fsm.STATES[state])
        target = fsm.EVENTS[event]

        mock_state.side_effect = [state, target]

        response = auth_client.post(
            self.endpoint, data={"event": event, "current_state": state}
        )
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        assert response.context["current_state"] == target
        assert response.context["events"] == fsm.STATES[target]
