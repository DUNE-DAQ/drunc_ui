"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from datetime import UTC, datetime, timedelta
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from druncschema.broadcast_pb2 import BroadcastMessage, BroadcastType
from kafka import KafkaConsumer

from ...models import DruncMessage

BROADCAST_TYPE_SEVERITY = {
    BroadcastType.ACK: "DEBUG",
    BroadcastType.RECEIVER_REMOVED: "INFO",
    BroadcastType.RECEIVER_ADDED: "INFO",
    BroadcastType.SERVER_READY: "INFO",
    BroadcastType.SERVER_SHUTDOWN: "INFO",
    BroadcastType.TEXT_MESSAGE: "INFO",
    BroadcastType.COMMAND_EXECUTION_START: "INFO",
    BroadcastType.COMMAND_RECEIVED: "INFO",
    BroadcastType.COMMAND_EXECUTION_SUCCESS: "INFO",
    BroadcastType.DRUNC_EXCEPTION_RAISED: "ERROR",
    BroadcastType.UNHANDLED_EXCEPTION_RAISED: "CRITICAL",
    BroadcastType.STATUS_UPDATE: "INFO",
    BroadcastType.SUBPROCESS_STATUS_UPDATE: "INFO",
    BroadcastType.DEBUG: "DEBUG",
    BroadcastType.CHILD_COMMAND_EXECUTION_START: "INFO",
    BroadcastType.CHILD_COMMAND_EXECUTION_SUCCESS: "INFO",
    BroadcastType.CHILD_COMMAND_EXECUTION_FAILED: "ERROR",
    BroadcastType.FSM_STATUS_UPDATE: "INFO",
}


class Command(BaseCommand):
    """Consumes messages from Kafka and stores them in the database."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("--debug", action="store_true")

    def handle(self, debug: bool = False, **kwargs: Any) -> None:  # type: ignore[misc]
        """Command business logic."""
        consumer = KafkaConsumer(bootstrap_servers=[settings.KAFKA_ADDRESS])
        consumer.subscribe(pattern=f"({'|'.join(settings.KAFKA_TOPIC_REGEX.values())})")
        # TODO: determine why the below doesn't work
        # consumer.subscribe(pattern="control.no_session.process_manager")

        self.stdout.write("Listening for messages from Kafka.")
        while True:
            for messages in consumer.poll(timeout_ms=500).values():
                message_records = []

                for message in messages:
                    if debug:
                        self.stdout.write(f"Message received: {message}")
                        self.stdout.flush()

                    # Convert Kafka timestamp (milliseconds) to datetime (seconds).
                    time = datetime.fromtimestamp(message.timestamp / 1e3, tz=UTC)

                    bm = BroadcastMessage()
                    bm.ParseFromString(message.value)
                    body = bm.data.value.decode("utf-8")

                    severity = BROADCAST_TYPE_SEVERITY.get(bm.type, "INFO")

                    message_records.append(
                        DruncMessage(
                            topic=message.topic,
                            timestamp=time,
                            message=body,
                            severity=severity,
                        )
                    )

                if message_records:
                    DruncMessage.objects.bulk_create(message_records)

            # Remove expired messages from the database.
            message_timeout = timedelta(seconds=settings.MESSAGE_EXPIRE_SECS)
            expire_time = datetime.now(tz=UTC) - message_timeout
            query = DruncMessage.objects.filter(timestamp__lt=expire_time)
            if query.count():
                if debug:
                    self.stdout.write(
                        f"Deleting {query.count()} messages "
                        f"older than {expire_time}."
                    )
                query.delete()
