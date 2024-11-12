from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse

from controller.fsm import DruncFSM
from controller.tables import FSMTable

from ...utils import LoginRequiredTest


class TestFSMView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("controller:state_machine")

    def test_empty_post(self, auth_client):
        """Tests basic calls of view method."""
        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        assert response.context["current_state"] == "None"
        assert response.context["events"] == [
            t.event for t in DruncFSM.get("none").current_state.transitions
        ]

    @pytest.mark.parametrize("state", DruncFSM.states)
    def test_non_empty_post(self, state, auth_client):
        """Tests basic calls of view method."""
        event = choice(DruncFSM.get(state.name).current_state.transitions)
        response = auth_client.post(
            self.endpoint, data={"event": event.event, "current_state": state.name}
        )
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        assert response.context["current_state"] == event.target.name
        assert response.context["events"] == [
            t.event for t in DruncFSM.get(event.target.name).current_state.transitions
        ]
