from http import HTTPStatus
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from process_manager.tables import ProcessTable

from ...utils import LoginRequiredTest


class TestProcessTableView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("process_manager:process_table")

    @pytest.mark.parametrize("method", ("get", "post"))
    def test_method(self, method, auth_client, mocker):
        """Tests basic calls of view method."""
        self._mock_session_info(mocker, [])
        response = getattr(auth_client, method)(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.context["table"], ProcessTable)

    def _mock_session_info(self, mocker, uuids):
        """Mocks views.get_session_info with ProcessInstanceList like data."""
        mock = mocker.patch("process_manager.views.partials.get_session_info")
        instance_mocks = [MagicMock() for uuid in uuids]
        for instance_mock, uuid in zip(instance_mocks, uuids):
            instance_mock.uuid.uuid = str(uuid)
            instance_mock.status_code = 0
        mock().data.values.__iter__.return_value = instance_mocks
        return mock

    def test_post_checked_rows(self, mocker, auth_client):
        """Tests table data is correct when post data is included."""
        all_uuids = [str(uuid4()) for _ in range(5)]
        selected_uuids = all_uuids[::2]

        self._mock_session_info(mocker, all_uuids)

        response = auth_client.post(self.endpoint, data=dict(select=selected_uuids))
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, ProcessTable)

        for row in table.data.data:
            assert row["checked"] == (row["uuid"] in selected_uuids)
        assert "checked" not in table.columns["select"].attrs["th__input"]

    def test_post_header_checked(self, mocker, auth_client):
        """Tests header checkbox is checked if all rows are checked."""
        all_uuids = [str(uuid4()) for _ in range(5)]
        selected_uuids = all_uuids

        self._mock_session_info(mocker, all_uuids)

        response = auth_client.post(self.endpoint, data=dict(select=selected_uuids))
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, ProcessTable)

        # All rows should be checked
        assert all(row["checked"] for row in table.data.data)

        # So header should be checked as well
        assert table.columns["select"].attrs["th__input"]["checked"] == "checked"


class TestMessagesView(LoginRequiredTest):
    """Test the process_manager.views.messages view function."""

    endpoint = reverse("process_manager:messages")

    def test_get(self, auth_client):
        """Tests basic calls of view method."""
        from datetime import UTC, datetime, timedelta

        from main.models import DruncMessage

        t1 = datetime.now(tz=UTC)
        t2 = t1 + timedelta(minutes=10)
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(timestamp=t1, message="message 0"),
                DruncMessage(timestamp=t2, message="message 1"),
            ]
        )

        with assertTemplateUsed("process_manager/partials/message_items.html"):
            response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

        # messages have been added to the context in reverse order
        t1_str = t1.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][1] == f"{t1_str}: message 0"
        t2_str = t2.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][0] == f"{t2_str}: message 1"
