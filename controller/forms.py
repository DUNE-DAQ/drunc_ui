"""Module to create a Django form from a list of Arguments."""

from enum import IntEnum

from django.forms import BooleanField, CharField, Field, FloatField, Form, IntegerField
from druncschema.controller_pb2 import Argument


class Presence(IntEnum):
    """Enum to represent the presence of an argument."""

    MANDATORY = 0
    OPTIONAL = 1


class FieldType(IntEnum):
    """Enum to represent the type of an argument."""

    INT = 0
    FLOAT = 1
    STRING = 2
    BOOL = 3


def get_form_from_arguments(data: list[Argument]) -> type[Form]:
    """Creates a form from a list of Arguments.

    Args:
        data: List of Arguments.

    Returns:
        A form class including the required arguments.
    """
    fields: dict[str, Field] = {}
    for item in data:
        name = item.name
        mandatory = item.presence == Presence.MANDATORY
        initial = item.default_value.value.decode()
        match item.type:
            case FieldType.INT:
                fields[name] = IntegerField(required=mandatory, initial=initial)
            case FieldType.FLOAT:
                fields[name] = FloatField(required=mandatory, initial=initial)
            case FieldType.STRING:
                fields[name] = CharField(required=mandatory, initial=initial)
            case FieldType.BOOL:
                fields[name] = BooleanField(required=mandatory, initial=initial)

    return type("DynamicForm", (Form,), fields)
