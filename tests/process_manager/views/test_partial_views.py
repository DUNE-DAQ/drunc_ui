from http import HTTPStatus
from unittest.mock import MagicMock
from uuid import uuid4

from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from process_manager.tables import ProcessTable

from ...utils import LoginRequiredTest


class TestProcessTableView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("process_manager:process_table")

    def test_get(self, auth_client, mocker):
        """Tests basic calls of view method."""
        uuids = [str(uuid4()) for _ in range(5)]
        self._mock_session_info(mocker, uuids)
        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, ProcessTable)
        assert all(row["uuid"] == uuid for row, uuid in zip(table.data.data, uuids))

    def _mock_session_info(self, mocker, uuids):
        """Mocks views.get_session_info with ProcessInstanceList like data."""
        mock = mocker.patch("process_manager.views.partials.get_session_info")
        instance_mocks = [MagicMock() for uuid in uuids]
        for instance_mock, uuid in zip(instance_mocks, uuids):
            instance_mock.uuid.uuid = str(uuid)
            instance_mock.status_code = 0
        mock().data.values.__iter__.return_value = instance_mocks
        return mock


class TestMessagesView(LoginRequiredTest):
    """Test the process_manager.views.messages view function."""

    endpoint = reverse("process_manager:messages")

    def test_get(self, auth_client):
        """Tests basic calls of view method."""
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.sessions.models import Session

        session = Session.objects.get()
        message_data = ["message 1", "message 2"]
        store = SessionStore(session_key=session.session_key)
        store["messages"] = message_data
        store.save()

        with assertTemplateUsed("process_manager/partials/message_items.html"):
            response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

        # messages have been removed from the session and added to the context
        assert response.context["messages"] == message_data[::-1]
        assert "messages" not in store.load()
