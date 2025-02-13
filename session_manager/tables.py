"""Tables to display session manager data."""

from typing import ClassVar

import django_tables2 as tables


class ActiveSessions(tables.Table):
    """Defines a table for the active sessions data."""

    name = tables.Column(
        verbose_name="Session Name",
        attrs={
            "td": {
                "class": "text-break text-start small-text",
                "style": "width:300px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    actor = tables.Column(
        verbose_name="Actor",
        attrs={
            "td": {
                "class": "text-primary text-start small-text",
                "style": "width:200px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    class Meta:
        """Table meta options for rendering behaviour and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive small-text",
        }


class AvailableConfigs(tables.Table):
    """Defines a table for the available configurations."""

    file = tables.Column(
        verbose_name="Configuration File",
        attrs={
            "td": {
                "class": "text-break text-start small-text",
                "style": "width:300px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    id = tables.Column(
        verbose_name="ID",
        attrs={
            "td": {
                "class": "text-primary text-start small-text",
                "style": "width:200px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    class Meta:
        """Table meta options for rendering behaviour and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive small-text",
        }
