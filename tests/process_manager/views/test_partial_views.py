from http import HTTPStatus
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse

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

    def _mock_session_info(self, mocker, uuids, sessions: list[str] = []):
        """Mocks views.get_session_info with ProcessInstanceList like data."""
        mock = mocker.patch("process_manager.views.partials.get_session_info")
        instance_mocks = [MagicMock() for _ in uuids]
        sessions = sessions or [f"session{i}" for i in range(len(uuids))]

        for instance_mock, uuid, session in zip(instance_mocks, uuids, sessions):
            instance_mock.uuid.uuid = str(uuid)
            instance_mock.process_description.metadata.session = (
                session  # Correctly set the session attribute
            )
            instance_mock.status_code = 0

        mock().data.values.__iter__.return_value = instance_mocks
        return mock

    def test_get_with_search(self, auth_client: Client, mocker):
        """Tests basic calls of view method."""
        uuids = [str(uuid4()) for _ in range(5)]
        sessions = ["session1", "session2", "session2", "session2", "session3"]
        self._mock_session_info(mocker, uuids, sessions)

        # Perform the search request using 'search-drp' and 'search' parameters
        response = auth_client.get(
            self.endpoint, data={"search-drp": "session", "search": "session2"}
        )
        assert response.status_code == HTTPStatus.OK

        # Retrieve the filtered table data
        table = response.context["table"]
        assert isinstance(table, ProcessTable)

        # Check that each row in the table contains "session2" as the session value
        for row in table.data.data:
            assert (
                row["session"] == "session2"
            ), f"Expected 'session2', got '{row['session']}'"


process_1 = {
    "uuid": "1",
    "name": "Process1",
    "user": "user1",
    "session": "session1",
    "status_code": "running",
    "exit_code": 0,
}
process_2 = {
    "uuid": "2",
    "name": "Process2",
    "user": "user2",
    "session": "session2",
    "status_code": "completed",
    "exit_code": 0,
}


@pytest.mark.parametrize(
    "search, column, table, expected",
    [
        pytest.param(
            "",
            "",
            [process_1, process_2],
            [process_1, process_2],
            id="no search",
        ),
        pytest.param(
            "Process1",
            "",
            [process_1, process_2],
            [process_1],
            id="search all columns",
        ),
        pytest.param(
            "Process1",
            "name",
            [process_1, process_2],
            [process_1],
            id="search specific column",
        ),
        pytest.param(
            "Process1",
            "nonexistent",
            [process_1, process_2],
            [process_1],
            id="search non-existent column",
        ),
        pytest.param(
            "Process1",
            "",
            [],
            [],
            id="filter empty table",
        ),
        pytest.param(
            "process1",
            "",
            [process_1, process_2],
            [process_1],
            id="search case insensitive",
        ),
    ],
)
def test_filter_table(search, column, table, expected):
    """Test filter_table function."""
    from process_manager.views.partials import filter_table

    assert filter_table(search, column, table) == expected
