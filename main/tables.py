"""Defines the Drunc Message Table for the data from the Kafka messages."""

import django_tables2 as tables


class DruncMessageTable(tables.Table):
    """Defines a Drunc Message Table for the data from the Kafka messages."""

    timestamp = tables.DateTimeColumn(format="Y-m-d h:m:s")
    severity = tables.Column(verbose_name="Severity", orderable=True)
    message = tables.Column(verbose_name="Message", orderable=False)
