"""Defines the FSMTable for displaying the FSM in a structured table format."""

from typing import ClassVar

import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe


class FSMTable(tables.Table):
    """Defines a table for the data from the FSM."""

    state = tables.Column(
        verbose_name="State",
        default=" ",
        attrs={
            "td": {"class": "text-secondary text-start"},
            "th": {"class": "header-style"},
        },
    )

    transition = tables.Column(
        verbose_name="Transition",
        default=" ",
        attrs={
            "th": {"class": "text-center header-style"},
        },
    )

    arrow = tables.Column(
        verbose_name="",
        default=" ",
        attrs={"td": {"class": "fw-bold text-break text-start"}},
    )

    target = tables.Column(
        verbose_name="Target",
        default=" ",
        attrs={
            "td": {"class": "text-secondary text-start"},
            "th": {"class": "header-style"},
        },
    )

    class Meta:
        """Table meta options for rendering behavior and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive",
        }

    @classmethod
    def from_dict(
        cls, states: dict[str, list[dict[str, str]]], current_state: str
    ) -> str:
        """Create the FSM table from the states dictionary.

        Args:
            states (dict[str, list[dict[str, str]]): The FSM states and events.
            current_state (str): The current state of the FSM.

        Returns:
            str: The rendered FSM table.
        """
        table_data = []
        for state, events in states.items():
            current = state == current_state
            table_data.append(
                {
                    "state": toggle_text(state, current),
                }
            )
            for event in events:
                table_data.append(
                    {
                        "transition": toggle_button(event["event"], current),
                        "arrow": "→",
                        "target": toggle_text(event["target"], current),
                    }
                )
        return cls(table_data)


def toggle_text(text: str, current: bool) -> str:
    """Enable the text."""
    if not current:
        return text.upper()
    return mark_safe(f'<span class="fw-bold text-primary">{text.upper()}</span>')


def toggle_button(event: str, current: bool) -> str:
    """Enable the text as a button.

    Args:
        event (str): The text to display.
        current (bool): Whether the event is the current state.

    Returns:
        str: The button as a safe string.
    """
    if current:
        action = f"hx-post={reverse('controller:state_machine')} hx-target='#state-machine' hx-include='#event_{event}'"  # noqa: E501
        return mark_safe(
            f"<button {action} class='btn btn-success w-100 mx-2' >{event}</button>"
        )
    return mark_safe(
        f"<button disabled class='btn btn-secondary w-100 mx-2'>{event}</button>"
    )
