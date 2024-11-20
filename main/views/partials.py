"""View functions for partials."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig

from main.models import DruncMessage
from main.tables import DruncMessageTable
from main.views.utils import handle_errors


@login_required
@handle_errors
def messages(request: HttpRequest, topic: str) -> HttpResponse:
    """View function to display messages for a given topic."""
    search = request.GET.get("search", "")
    severity = request.GET.get("severity", "")

    records = DruncMessage.objects.filter(
        topic__regex=settings.KAFKA_TOPIC_REGEX[topic], message__icontains=search
    ).order_by("-timestamp")

    if severity:
        records = records.filter(severity=severity)

    table = DruncMessageTable(records)
    RequestConfig(request, paginate=False).configure(table)

    return render(
        request=request,
        context={"table": table},
        template_name="main/partials/message_items.html",
    )
