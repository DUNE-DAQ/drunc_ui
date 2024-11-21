"""Module to create a Django form from a list of Arguments."""

from django.forms import BooleanField, CharField, Field, FloatField, Form, IntegerField

from . import controller_interface as ci


def get_form_for_event(event: str) -> type[Form]:
    """Creates a form from a list of Arguments.

    Args:
        event: Event to get the form for.

    Returns:
        A form class including the required arguments.
    """
    data = ci.get_arguments(event)
    fields: dict[str, Field] = {}
    for item in data:
        name = item.name
        mandatory = item.presence == ci.Presence.MANDATORY
        # Remove the new line and end of string characters causing trouble
        # when submitting the form
        initial = item.default_value.value.decode().strip().replace(chr(4), "")
        match item.type:
            case ci.FieldType.INT:
                fields[name] = IntegerField(required=mandatory, initial=initial)
            case ci.FieldType.FLOAT:
                fields[name] = FloatField(required=mandatory, initial=initial)
            case ci.FieldType.STRING:
                fields[name] = CharField(required=mandatory, initial=initial)
            case ci.FieldType.BOOL:
                fields[name] = BooleanField(required=mandatory, initial=initial)

    return type("DynamicForm", (Form,), fields)
