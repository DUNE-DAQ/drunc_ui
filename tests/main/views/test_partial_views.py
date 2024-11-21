from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from main.models import DruncMessage
from main.tables import DruncMessageTable

from ...utils import LoginRequiredTest


class TestMessagesView(LoginRequiredTest):
    """Test the main.views.messages view function."""

    endpoint = reverse("main:messages", args=["PROCMAN"])
    topic = "control.test.process_manager"

    @pytest.fixture(autouse=True)
    def kafka_topic_regex(self, settings):
        """Set Kafka topic regex patterns for tests."""
        settings.KAFKA_TOPIC_REGEX["PROCMAN"] = r"^control\..+\.process_manager$"

    def test_get(self, auth_client):
        """Test that the view returns messages in a table."""
        t1 = datetime.now(tz=UTC)
        t2 = t1 + timedelta(minutes=10)
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(
                    topic=self.topic, timestamp=t1, message="message 0", severity="INFO"
                ),
                DruncMessage(
                    topic=self.topic,
                    timestamp=t2,
                    message="message 1",
                    severity="ERROR",
                ),
            ]
        )

        with assertTemplateUsed("main/partials/message_items.html"):
            response = auth_client.get(self.endpoint)

        assert response.status_code == HTTPStatus.OK
        assert "table" in response.context
        table = response.context["table"]
        assert isinstance(table, DruncMessageTable)

        table_data = list(table.data)
        assert len(table_data) == 2

        # Assert that the messages are in the correct order
        assert table_data[0].timestamp == t2
        assert table_data[0].message == "message 1"
        assert table_data[0].severity == "ERROR"

        assert table_data[1].timestamp == t1
        assert table_data[1].message == "message 0"
        assert table_data[1].severity == "INFO"

    def test_get_with_search(self, auth_client):
        """Test message filtering based on search query."""
        t = datetime.now(tz=UTC)
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(
                    topic=self.topic,
                    timestamp=t,
                    message="her message",
                    severity="INFO",
                ),
                DruncMessage(
                    topic=self.topic,
                    timestamp=t,
                    message="HIs meSsaGe",
                    severity="DEBUG",
                ),
            ]
        )

        # Search for "his message"
        response = auth_client.get(self.endpoint, data={"search": "his message"})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        table_data = list(table.data)
        assert len(table_data) == 1
        assert table_data[0].message == "HIs meSsaGe"

        # Search for "MESS"
        response = auth_client.get(self.endpoint, data={"search": "MESS"})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        table_data = list(table.data)
        assert len(table_data) == 2

        messages = [row.message for row in table_data]
        assert "her message" in messages
        assert "HIs meSsaGe" in messages

        # Search for "not there"
        response = auth_client.get(self.endpoint, data={"search": "not there"})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        table_data = list(table.data)
        assert len(table_data) == 0

    def test_get_wrong_topic(self, auth_client):
        """Test that messages with non-matching topics are not included."""
        DruncMessage.objects.create(
            topic="the.wrong.topic",
            timestamp=datetime.now(tz=UTC),
            message="message",
            severity="INFO",
        )

        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        table_data = list(table.data)
        assert len(table_data) == 0
