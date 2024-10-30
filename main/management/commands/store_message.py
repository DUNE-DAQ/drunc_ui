"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from datetime import UTC, datetime
from typing import Any

from django.core.management.base import BaseCommand

from ...models import DruncMessage


class Command(BaseCommand):
    """Store Kafka messages in the database."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("-t", "--topic", default="NO_TOPIC")
        parser.add_argument("-m", "--message", default="NO_MESSAGE")

    def handle(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[misc]
        """Command business logic."""
        topic = kwargs["topic"]
        message = kwargs["message"]
        timestamp = datetime.now(tz=UTC)
        DruncMessage.objects.create(topic=topic, timestamp=timestamp, message=message)
