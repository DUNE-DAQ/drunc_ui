from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from main.models import DruncMessage

from ...utils import LoginRequiredTest


class TestMessagesView(LoginRequiredTest):
    """Test the main.views.messages view function."""

    endpoint = reverse("main:messages", args=["PROCMAN"])
    topic = "control.test.process_manager"

    @pytest.fixture(autouse=True)
    def kafka_topic_regex(self, settings):
        """Set Kafka topic regex patterns for tests."""
        settings.KAFKA_TOPIC_REGEX["PROCMAN"] = "^control\..+\.process_manager$"

    def test_get(self, auth_client):
        """Tests basic calls of view method."""
        t1 = datetime.now(tz=UTC)
        t2 = t1 + timedelta(minutes=10)
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(topic=self.topic, timestamp=t1, message="message 0"),
                DruncMessage(topic=self.topic, timestamp=t2, message="message 1"),
            ]
        )

        with assertTemplateUsed("main/partials/message_items.html"):
            response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

        # messages have been added to the context in reverse order
        t1_str = t1.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][1] == f"{t1_str}: message 0"
        t2_str = t2.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][0] == f"{t2_str}: message 1"

    def test_get_with_search(self, auth_client):
        """Tests message filtering of view method."""
        t = datetime.now(tz=UTC)
        t_str = t.strftime("%Y-%m-%d %H:%M:%S")
        her_msg = "her message"
        his_msg = "HIs meSsaGe"
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(topic=self.topic, timestamp=t, message=her_msg),
                DruncMessage(topic=self.topic, timestamp=t, message=his_msg),
            ]
        )

        # search for "his message"
        response = auth_client.get(self.endpoint, data={"search": "his message"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 1
        assert response.context["messages"][0] == f"{t_str}: {his_msg}"

        # search for "MESS"
        response = auth_client.get(self.endpoint, data={"search": "MESS"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 2
        assert response.context["messages"][0] == f"{t_str}: {his_msg}"
        assert response.context["messages"][1] == f"{t_str}: {her_msg}"

        # search for "not there"
        response = auth_client.get(self.endpoint, data={"search": "not there"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 0

    def test_get_wrong_topic(self, auth_client):
        """Test view method plays nice with other Kafka topics."""
        DruncMessage.objects.create(
            topic="the.wrong.topic", timestamp=datetime.now(tz=UTC), message="message"
        )

        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 0
